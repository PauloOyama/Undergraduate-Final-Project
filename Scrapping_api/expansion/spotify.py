"""Cliente mínimo da Web API do Spotify (Client Credentials) para descobrir faixas.

Só usa endpoints que ainda respondem: Search, Artist's Albums, Album Tracks, Get Artist e
Get Track. Os endpoints em lote (?ids=) são tentados primeiro e, se o Spotify os fechar para
o app (como fez em fev/2026 para apps novos), o cliente passa a pedir um item por vez.
"""

import os
import time
from typing import Dict, Iterable, Iterator, List, Optional

from .http import HttpClient

API = "https://api.spotify.com/v1"


class SpotifyClient:
    def __init__(self, http: HttpClient, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.http = http
        self.client_id = client_id or os.environ["SPOTIPY_CLIENT_ID"]
        self.client_secret = client_secret or os.environ["SPOTIPY_CLIENT_SECRET"]
        self._token = None
        self._token_expires = 0.0
        self.search_limit = 50          # cai para 10 se o app estiver nas regras novas
        self.batch_ok = True            # cai para False se ?ids= deixar de funcionar

    # -- autenticação -------------------------------------------------------------------
    def _headers(self) -> Dict[str, str]:
        if not self._token or time.time() > self._token_expires - 60:
            resp = self.http.session.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data["access_token"]
            self._token_expires = time.time() + data.get("expires_in", 3600)
        return {"Authorization": "Bearer " + self._token}

    def get(self, path: str, **params):
        resp = self.http.get(API + path, params=params, headers=self._headers())
        if resp.status_code == 401:            # token expirou no meio do caminho
            self._token = None
            resp = self.http.get(API + path, params=params, headers=self._headers())
        return resp

    # -- descoberta ---------------------------------------------------------------------
    def search(self, query: str, kind: str, market: str, max_items: int) -> Iterator[dict]:
        """Pagina a busca até acabar os resultados, o offset 1000 ou max_items.

        O campo `total` da busca não é confiável hoje (fica em 100), então a paginação
        para quando uma página volta vazia.
        """
        seen = 0
        offset = 0
        while seen < max_items and offset < 1000:
            limit = min(self.search_limit, max_items - seen, 1000 - offset)
            resp = self.get("/search", q=query, type=kind, market=market, limit=limit, offset=offset)
            if resp.status_code == 400 and self.search_limit > 10:
                self.search_limit = 10
                continue
            if not resp.ok:
                break
            items = [i for i in resp.json().get(kind + "s", {}).get("items", []) if i]
            if not items:
                break
            for item in items:
                yield item
            seen += len(items)
            offset += len(items)

    def artist_albums(self, artist_id: str, market: str, max_albums: int) -> List[dict]:
        resp = self.get(f"/artists/{artist_id}/albums", include_groups="album,single",
                        market=market, limit=min(max_albums, 50 if self.search_limit > 10 else 10))
        if not resp.ok:
            return []
        return resp.json().get("items", [])[:max_albums]

    def album_tracks(self, album_id: str, market: str) -> List[dict]:
        resp = self.get(f"/albums/{album_id}/tracks", market=market, limit=50 if self.search_limit > 10 else 10)
        if not resp.ok:
            return []
        return resp.json().get("items", [])

    def tracks(self, ids: List[str], market: str) -> List[dict]:
        """Faixas completas (com ISRC e, quando o app ainda recebe, popularidade)."""
        return self._several("/tracks", "tracks", ids, 50, market=market)

    def artists(self, ids: List[str]) -> List[dict]:
        """Artistas completos (com gêneros)."""
        return self._several("/artists", "artists", ids, 50)

    def _several(self, path: str, key: str, ids: List[str], size: int, **params) -> List[dict]:
        out = []
        for chunk in _chunks(ids, size):
            if self.batch_ok:
                resp = self.get(path, ids=",".join(chunk), **params)
                if resp.ok:
                    out += [x for x in resp.json().get(key, []) if x]
                    continue
                if resp.status_code in (403, 404):
                    self.batch_ok = False   # o endpoint em lote foi fechado para este app
            for one in chunk:
                resp = self.get(f"{path}/{one}", **params)
                if resp.ok:
                    out.append(resp.json())
        return out


def _chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i:i + size]
