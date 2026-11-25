"""Fluxo de expansão da base: busca estratificada -> álbuns dos artistas -> ISRC e gêneros ->
atributos de áudio -> remoção de duplicatas -> CSV no formato da base do TCC.

Cada etapa salva o progresso em `data_dir` e pode ser interrompida e retomada: consultas e
artistas já processados ficam em state.json (o mesmo papel do prefixo OK_ dos scripts antigos).
"""

import csv
import json
import os
import threading
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .features import FEATURES, reccobeats_features
from .http import HttpClient
from .lastfm import LastFm
from .spotify import SpotifyClient

ROOT = Path(__file__).resolve().parents[2]
SCRAPPING = ROOT / "Scrapping_api"
DATASET_DIR = ROOT / "Understanding_Spotify_Metadata" / "DataSet"
OLD_BASE = DATASET_DIR / "metadata_worth_tracks.csv"
OLD_GENRES = DATASET_DIR / "DataSet_With_Genre.csv"

# Gêneros que a base antiga quase não tem (ela cresceu a partir de sementes de rock, MPB e rap).
MISSING_GENRES = ["forro", "funk carioca", "axe", "pagode", "piseiro", "brega", "jazz", "bossa nova",
                  "electronic", "house", "techno", "reggaeton", "salsa", "cumbia", "afrobeats",
                  "amapiano", "j-pop", "anime", "reggae", "blues", "soul", "gospel", "country",
                  "classical", "metal", "punk", "folk", "flamenco", "fado", "k-pop"]
DECADES = [1960, 1970, 1980, 1990, 2000, 2010, 2020]
MARKETS = ["BR", "US", "MX", "GB", "JP", "NG", "KR"]

STEPS = ["search", "artists", "enrich", "features", "export"]


class Expansion:
    def __init__(self, data_dir: Optional[Path] = None, progress: Optional[Callable[[dict], None]] = None):
        self.data_dir = Path(data_dir or SCRAPPING / "expansion_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.progress = progress or (lambda event: None)
        self.http = HttpClient(log=lambda msg: self.emit(message=msg))
        self.spotify = SpotifyClient(self.http)
        self.lastfm = LastFm(self.http)
        self.stop = threading.Event()
        self.state = self._load("state.json", {"queries_done": [], "artists_done": [], "log": []})
        self.tracks: Dict[str, dict] = self._load("tracks.json", {})
        self.artists: Dict[str, dict] = self._load("artists.json", {})
        self.step = None

    # -- persistência --------------------------------------------------------------------
    def _load(self, name: str, default):
        path = self.data_dir / name
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return default

    def save(self):
        for name, obj in (("state.json", self.state), ("tracks.json", self.tracks), ("artists.json", self.artists)):
            tmp = self.data_dir / (name + ".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False)
            os.replace(tmp, self.data_dir / name)

    def emit(self, **event):
        event.setdefault("step", self.step)
        event["counters"] = self.counters()
        if event.get("message"):
            self.state["log"] = (self.state.get("log", []) + [
                {"at": datetime.now().isoformat(timespec="seconds"), "step": self.step, "message": event["message"]}
            ])[-200:]
        self.progress(event)

    def counters(self) -> dict:
        tracks = self.tracks.values()
        return {
            "tracks": len(self.tracks),
            "artists": len(self.artists),
            "with_isrc": sum(1 for t in tracks if t.get("isrc")),
            "with_features": sum(1 for t in tracks if t.get("features")),
            "queries_done": len(self.state["queries_done"]),
            "artists_done": len(self.state["artists_done"]),
            "api_calls": self.http.calls,
        }

    # -- 1. busca estratificada ------------------------------------------------------------
    def plan_queries(self, genres: Optional[List[str]] = None, top_genres: int = 40,
                     decades: Optional[List[int]] = None, markets: Optional[List[str]] = None,
                     cap: int = 200) -> List[dict]:
        """A grade: gênero (sozinho e por década) e ano por mercado.

        A busca por gênero sozinho para em cerca de 160 faixas e algumas combinações de gênero
        com década voltam vazias (ex. genre:mpb year:1970-1979), por isso a grade mistura as
        três formas e o teto `cap` por célula mantém o equilíbrio.
        """
        genres = genres or (self.old_top_genres(top_genres) + MISSING_GENRES)
        genres = list(dict.fromkeys(g.lower() for g in genres))
        decades = decades or DECADES
        markets = markets or MARKETS
        cells = []
        for g in genres:
            cells.append({"query": f"genre:{g}", "market": "BR", "cap": cap, "kind": "genre"})
            for d in decades:
                cells.append({"query": f"genre:{g} year:{d}-{d + 9}", "market": "BR", "cap": cap, "kind": "genre+decade"})
        for m in markets:
            for d in decades:
                for y in range(d, min(d + 10, datetime.now().year + 1), 3):
                    cells.append({"query": f"year:{y}", "market": m, "cap": cap // 2, "kind": "year+market"})
        for c in cells:
            c["id"] = f'{c["market"]}|{c["query"]}'
            if c["kind"] == "genre+decade":
                c["genre_cell"] = f'BR|genre:{c["query"].split(" year:")[0][6:]}'
        # Primeiro todos os gêneros sozinhos, depois ano por mercado, por último gênero por década:
        # rodando só uma parte da grade, a base já sai variada.
        order = {"genre": 0, "year+market": 1, "genre+decade": 2}
        return sorted(cells, key=lambda c: order[c["kind"]])

    def old_top_genres(self, n: int) -> List[str]:
        counts = Counter()
        for f in (SCRAPPING / "artists").glob("*.json"):
            with open(f, encoding="utf-8") as fh:
                for a in json.load(fh).get("artists", []):
                    counts.update(a.get("genres", []))
        return [g for g, _ in counts.most_common(n)]

    def run_search(self, cells: List[dict], max_cells: Optional[int] = None):
        self.step = "search"
        done = set(self.state["queries_done"])
        todo = [c for c in cells if c["id"] not in done][:max_cells]
        yields = self.state.setdefault("yields", {})
        for i, cell in enumerate(todo, 1):
            if self.stop.is_set():
                break
            # gênero com pouco resultado sozinho também não rende por década: pula a célula
            if yields.get(cell.get("genre_cell"), 999) < 50:
                self.state["queries_done"].append(cell["id"])
                self.emit(done=i, total=len(todo), message=f'{cell["query"]}: pulada (o gênero sozinho rendeu pouco)')
                continue
            new = 0
            found = 0
            for item in self.spotify.search(cell["query"], "track", cell["market"], cell["cap"]):
                found += 1
                if item["id"] not in self.tracks:
                    self.tracks[item["id"]] = self._track_record(item, cell)
                    new += 1
                for a in item["artists"]:
                    self.artists.setdefault(a["id"], {"id": a["id"], "name": a["name"]})
            yields[cell["id"]] = found
            self.state["queries_done"].append(cell["id"])
            self.emit(done=i, total=len(todo), message=f'{cell["query"]} ({cell["market"]}): {new} faixas novas')
            if i % 10 == 0:
                self.save()
        self.save()

    # -- 2. álbuns dos artistas (no lugar do top tracks) -----------------------------------
    def run_artists(self, max_artists: Optional[int] = None, albums_per_artist: int = 4,
                    tracks_per_artist: int = 5, market: str = "BR"):
        """Para cada artista novo, pega faixas de vários álbuns e singles (não só as mais tocadas),
        com teto por artista para nenhum dominar a base."""
        self.step = "artists"
        done = set(self.state["artists_done"])
        todo = [a for a in self.artists if a not in done][:max_artists]
        for i, artist_id in enumerate(todo, 1):
            if self.stop.is_set():
                break
            have = sum(1 for t in self.tracks.values() if artist_id in t["artist_ids"])
            room = max(0, tracks_per_artist - have)
            added = 0
            if room:
                for album in self.spotify.artist_albums(artist_id, market, albums_per_artist):
                    if added >= room:
                        break
                    for item in self.spotify.album_tracks(album["id"], market)[:2]:   # 2 por álbum
                        if added >= room:
                            break
                        if item["id"] not in self.tracks and artist_id in [a["id"] for a in item["artists"]]:
                            item["album"] = album
                            self.tracks[item["id"]] = self._track_record(item, {"query": "artist-albums", "market": market})
                            added += 1
            self.state["artists_done"].append(artist_id)
            self.emit(done=i, total=len(todo), message=f'{self.artists[artist_id]["name"]}: {added} faixas de álbuns')
            if i % 25 == 0:
                self.save()
        self.save()

    # -- 3. ISRC, popularidade e gêneros ------------------------------------------------------
    def run_enrich(self, market: str = "BR"):
        self.step = "enrich"
        ids = [tid for tid, t in self.tracks.items() if "isrc" not in t]
        for i in range(0, len(ids), 50):
            if self.stop.is_set():
                break
            for full in self.spotify.tracks(ids[i:i + 50], market):
                t = self.tracks.get(full["id"])
                if t is not None:
                    t["isrc"] = (full.get("external_ids") or {}).get("isrc")
                    t["popularity"] = full.get("popularity")
            self.emit(done=min(i + 50, len(ids)), total=len(ids), message=f"ISRC de {min(i + 50, len(ids))} de {len(ids)} faixas")
        missing = [aid for aid, a in self.artists.items() if "genres" not in a]
        for i in range(0, len(missing), 50):
            if self.stop.is_set():
                break
            for full in self.spotify.artists(missing[i:i + 50]):
                a = self.artists.get(full["id"])
                if a is not None:
                    a["genres"] = full.get("genres", [])
                    a["popularity"] = full.get("popularity")
            self.emit(done=min(i + 50, len(missing)), total=len(missing),
                      message=f"gêneros de {min(i + 50, len(missing))} de {len(missing)} artistas")
        if self.lastfm.enabled:
            for aid, a in list(self.artists.items()):
                if self.stop.is_set():
                    break
                if "listeners" not in a:
                    a["listeners"] = self.lastfm.listeners(a["name"])
        self.save()

    # -- 4. atributos de áudio --------------------------------------------------------------
    def run_features(self):
        self.step = "features"
        ids = [tid for tid, t in self.tracks.items() if "features" not in t]
        for i in range(0, len(ids), 200):
            if self.stop.is_set():
                break
            chunk = ids[i:i + 200]
            found = reccobeats_features(self.http, chunk)
            for tid in chunk:
                self.tracks[tid]["features"] = found.get(tid)   # None = o ReccoBeats não conhece
            self.emit(done=min(i + 200, len(ids)), total=len(ids),
                      message=f"atributos: {len(found)} de {len(chunk)} faixas encontradas no ReccoBeats")
            self.save()
        self.save()

    # -- 5. duplicatas e CSV ----------------------------------------------------------------
    def run_export(self, max_per_artist: int = 8) -> dict:
        self.step = "export"
        old_uris = set()
        if OLD_BASE.exists():
            with open(OLD_BASE, encoding="utf-8") as f:
                old_uris = {r["uri"] for r in csv.DictReader(f)}
        rows, seen_isrc, per_artist = [], set(), Counter()
        skipped = Counter()
        for t in sorted(self.tracks.values(), key=lambda t: -(t.get("popularity") or 0)):
            if not t.get("features"):
                skipped["sem atributos"] += 1
                continue
            if t["uri"] in old_uris:
                skipped["já na base antiga"] += 1
                continue
            if t.get("isrc") and t["isrc"] in seen_isrc:
                skipped["mesmo ISRC"] += 1
                continue
            lead = t["artist_ids"][0]
            if per_artist[lead] >= max_per_artist:
                skipped["teto por artista"] += 1
                continue
            seen_isrc.add(t.get("isrc"))
            per_artist[lead] += 1
            genres = self.artists.get(lead, {}).get("genres") or []
            rows.append({
                "popularity": t.get("popularity"), "name": t["name"], "track_id": t["id"], "uri": t["uri"],
                **t["features"], "duration_ms": t["duration_ms"], "time_signature": "",
                "created_at": datetime.now().isoformat(sep=" ", timespec="seconds"),
                "artists": "; ".join(t["artist_names"]), "genres": "; ".join(genres),
                "release_year": t.get("release_year"), "isrc": t.get("isrc"), "market": t["market"],
                "source": t["source"],
            })
        out = DATASET_DIR / "expansion_tracks.csv"
        columns = ["popularity", "name", "track_id", "uri", "acousticness", "danceability", "duration_ms",
                   "energy", "instrumentalness", "key", "loudness", "liveness", "mode", "speechiness", "tempo",
                   "time_signature", "valence", "created_at", "artists", "genres", "release_year", "isrc",
                   "market", "source"]
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        summary = {"exported": len(rows), "skipped": dict(skipped), "file": str(out.relative_to(ROOT))}
        self.state["last_export"] = summary
        self.emit(done=1, total=1, message=f"{len(rows)} faixas novas salvas em {summary['file']}")
        self.save()
        return summary

    # -- utilidades ---------------------------------------------------------------------
    @staticmethod
    def _track_record(item: dict, cell: dict) -> dict:
        album = item.get("album") or {}
        year = (album.get("release_date") or "")[:4]
        return {
            "id": item["id"], "uri": item["uri"], "name": item["name"],
            "artist_ids": [a["id"] for a in item["artists"]], "artist_names": [a["name"] for a in item["artists"]],
            "album": album.get("name"), "release_year": int(year) if year.isdigit() else None,
            "duration_ms": item.get("duration_ms"), "market": cell["market"], "source": cell["query"],
        }
