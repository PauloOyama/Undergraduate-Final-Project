"""Relatório de diversidade: compara a base antiga com a base depois da expansão.

Métricas (todas sobre faixas):
- gêneros distintos e a fatia dos 5 gêneros mais comuns (concentração);
- índice de Herfindahl dos gêneros (0 = espalhado, 1 = um gênero só);
- índice de Gini de faixas por artista (0 = todos com o mesmo número, 1 = um artista com tudo);
- distribuição por década (só a base nova tem ano de lançamento) e por mercado;
- faixas de cauda longa (popularidade abaixo de 30).
"""

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

from .pipeline import DATASET_DIR, OLD_GENRES

csv.field_size_limit(10_000_000)


def _parse_genres(raw: str) -> List[str]:
    raw = (raw or "").strip()
    if raw.startswith("{"):                          # formato da base antiga: {"mpb","samba"}
        return [g.strip().strip('"') for g in raw.strip("{}").split(",") if g.strip().strip('"')]
    return [g.strip() for g in raw.split(";") if g.strip()]


def _gini(values: List[int]) -> float:
    values = sorted(values)
    n = len(values)
    if n == 0 or sum(values) == 0:
        return 0.0
    cum = sum((i + 1) * v for i, v in enumerate(values))
    return round((2 * cum) / (n * sum(values)) - (n + 1) / n, 3)


def summarize(rows: List[dict]) -> Dict:
    genre_counts, artist_counts, decades, markets = Counter(), Counter(), Counter(), Counter()
    long_tail = with_pop = 0
    for r in rows:
        genres = _parse_genres(r.get("genres", ""))
        if genres:
            genre_counts[genres[0]] += 1             # gênero principal do artista
        artist_counts[(r.get("artists") or "").split(";")[0].strip() or r.get("track_id")] += 1
        year = str(r.get("release_year") or "")
        if year[:4].isdigit():
            decades[f"{year[:3]}0s"] += 1
        if r.get("market"):
            markets[r["market"]] += 1
        pop = r.get("popularity")
        if pop not in (None, ""):
            with_pop += 1
            long_tail += float(pop) < 30
    total = sum(genre_counts.values()) or 1
    top5 = sum(c for _, c in genre_counts.most_common(5))
    hhi = sum((c / total) ** 2 for c in genre_counts.values())
    return {
        "tracks": len(rows),
        "artists": len(artist_counts),
        "genres": len(genre_counts),
        "top_genres": genre_counts.most_common(12),
        "top5_share": round(top5 / total, 3),
        "genre_hhi": round(hhi, 4),
        "gini_tracks_per_artist": _gini(list(artist_counts.values())),
        "decades": sorted(decades.items()),
        "markets": markets.most_common(),
        "long_tail_share": round(long_tail / with_pop, 3) if with_pop else None,
    }


def load_csv(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def report(write_to: Path = None) -> Dict:
    old = load_csv(OLD_GENRES)
    new = load_csv(DATASET_DIR / "expansion_tracks.csv")
    result = {"before": summarize(old), "added": summarize(new), "after": summarize(old + new)}
    if write_to:
        with open(write_to, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return result
