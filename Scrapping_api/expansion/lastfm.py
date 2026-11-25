"""Last.fm: artistas parecidos (no lugar do Related Artists) e ouvintes (no lugar da popularidade).

Opcional: só roda com LASTFM_API_KEY no .env (crie em https://www.last.fm/api/account/create).
"""

import os
from typing import List, Optional

from .http import HttpClient

API = "https://ws.audioscrobbler.com/2.0/"


class LastFm:
    def __init__(self, http: HttpClient, api_key: Optional[str] = None):
        self.http = http
        self.api_key = api_key or os.environ.get("LASTFM_API_KEY")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _call(self, method: str, **params) -> dict:
        resp = self.http.get(API, params={"method": method, "api_key": self.api_key, "format": "json", **params})
        return resp.json() if resp.ok else {}

    def similar_artists(self, name: str, limit: int = 20) -> List[str]:
        data = self._call("artist.getsimilar", artist=name, limit=limit, autocorrect=1)
        return [a["name"] for a in data.get("similarartists", {}).get("artist", [])]

    def listeners(self, name: str) -> Optional[int]:
        data = self._call("artist.getinfo", artist=name, autocorrect=1)
        value = data.get("artist", {}).get("stats", {}).get("listeners")
        return int(value) if value else None
