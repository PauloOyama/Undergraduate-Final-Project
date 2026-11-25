"""Atributos de áudio sem o Spotify.

O endpoint Audio Features do Spotify responde 403 para este app desde nov/2024. O ReccoBeats
aceita IDs do Spotify e devolve os mesmos atributos, no mesmo formato e com os mesmos valores
(conferido em "Something in the Orange": acousticness 0.555, energy 0.192, tempo 175.212),
então as faixas novas ficam comparáveis com as 39.948 da base antiga. Ele não devolve
time_signature, que o KNN_PCA.R já descarta.
"""

from typing import Dict, List

from .http import HttpClient

RECCOBEATS = "https://api.reccobeats.com/v1/audio-features"
FEATURES = ["acousticness", "danceability", "energy", "instrumentalness", "key", "liveness",
            "loudness", "mode", "speechiness", "tempo", "valence"]


def reccobeats_features(http: HttpClient, spotify_ids: List[str]) -> Dict[str, dict]:
    """Devolve {spotify_id: {atributos}} para as faixas que o ReccoBeats conhece (lotes de 40)."""
    found: Dict[str, dict] = {}
    for i in range(0, len(spotify_ids), 40):
        chunk = spotify_ids[i:i + 40]
        resp = http.get(RECCOBEATS, params={"ids": ",".join(chunk)})
        if not resp.ok:
            continue
        for row in resp.json().get("content", []):
            sid = (row.get("href") or "").rsplit("/", 1)[-1]
            if sid:
                found[sid] = {k: row.get(k) for k in FEATURES}
    return found
