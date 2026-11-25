from typing import Union, List
import requests
import json
import csv
from datetime import datetime
import spotipy
from fastapi import FastAPI

# uvicorn main:app --reload


def filterAudioFeatures(track_features: List, popularity: List) -> List[dict]:
    feat_tracks = []
    i = 0
    for feat in track_features:
        if feat is None:
            i = +1
            continue
        res = dict()
        res["popularity"] = popularity[i]
        res["danceability"] = feat["danceability"]
        res["energy"] = feat["energy"]
        res["key"] = feat["key"]
        res["loudness"] = feat["loudness"]
        res["mode"] = feat["mode"]
        res["speechiness"] = feat["speechiness"]
        res["acousticness"] = feat["acousticness"]
        res["instrumentalness"] = feat["instrumentalness"]
        res["liveness"] = feat["liveness"]
        res["valence"] = feat["valence"]
        res["tempo"] = feat["tempo"]
        res["track_id"] = feat["id"]
        res["uri"] = feat["uri"]
        res["duration_ms"] = feat["duration_ms"]
        res["time_signature"] = feat["time_signature"]
        i = +1
        feat_tracks.append(res)

    return feat_tracks


app = FastAPI()

import os
from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# Login do usuário (Authorization Code flow). O Redirect URI precisa estar
# cadastrado no Spotify Developer Dashboard exatamente igual a este.
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8000/callback")
SCOPE = "user-top-read playlist-modify-private user-library-read"
user_oauth = SpotifyOAuth(
    scope=SCOPE,
    redirect_uri=REDIRECT_URI,
    cache_handler=MemoryCacheHandler(),
    open_browser=False,
)
INDEX_PAGE = Path(__file__).parent / "index.html"


def get_user_token(q: Union[str, None] = None) -> str:
    """Usa o token passado em ?q= ou, se não houver, o token do login em /login."""
    if q:
        return q
    token_info = user_oauth.validate_token(user_oauth.cache_handler.get_cached_token())
    if not token_info:
        raise HTTPException(status_code=401, detail="Faça login em /login primeiro.")
    return token_info["access_token"]


@app.get("/")
def index():
    return FileResponse(INDEX_PAGE, media_type="text/html")


# Arquivos da página (CSS, JS, ícones) servidos ao lado do index.html.
FRONT_DIR = Path(__file__).parent
app.mount("/assets", StaticFiles(directory=FRONT_DIR / "assets"), name="assets")


@app.get("/favicon.svg")
def favicon():
    return FileResponse(FRONT_DIR / "favicon.svg", media_type="image/svg+xml")


@app.get("/login")
def login():
    return RedirectResponse(user_oauth.get_authorize_url())


@app.get("/callback")
def callback(code: Union[str, None] = None, error: Union[str, None] = None):
    if error or not code:
        raise HTTPException(status_code=400, detail=f"Login recusado: {error}")
    user_oauth.get_access_token(code, as_dict=False)
    return RedirectResponse("/")


@app.get("/status")
def status():
    token_info = user_oauth.validate_token(user_oauth.cache_handler.get_cached_token())
    if not token_info:
        return {"logged_in": False}
    me = spotipy.Spotify(auth=token_info["access_token"]).me()
    return {"logged_in": True, "user": me.get("display_name") or me["id"]}


def getMusicFeatures(ids: List):
    return spotify.audio_features(tracks=ids)


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    q = get_user_token(q)

    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": "Bearer " + q}
    response = requests.get(url, headers=headers)
    print(response.status_code)
    print(response.content)
    response_json = response.json()
    list_ids = []
    popularity = []
    for items in response_json["items"]:
        list_ids.append(items["id"])
        popularity.append(items["popularity"])
    res = getMusicFeatures(ids=list_ids)
    print(list_ids)
    tracks = filterAudioFeatures(res, popularity)
    path = f"../Understanding_Spotify_Metadata/my_account.csv"
    with open(path, "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tracks[0].keys())
        writer.writeheader()
        writer.writerows(tracks)
    return {"item_id": item_id, "q": q}


@app.get("/playlist/{item_id}")
def create_playlist(item_id: int, q: Union[str, None] = None):
    q = get_user_token(q)

    url_me = "https://api.spotify.com/v1/me"
    headers = {"Authorization": "Bearer " + q}
    response = requests.get(url_me, headers=headers)
    id_me = response.json()["id"]
    print(id_me)
    print("Pegou O ID")

    playlist = {"name": "TCC"}
    playlist["description"] = (
        "Para cada músicas das suas 20 mais ouvidas 2 serão recomendadas."
    )
    playlist["public"] = False

    url = "https://api.spotify.com/v1/users/{user_id}/playlists".format(user_id=id_me)
    response = requests.post(url=url, json=playlist, headers=headers)
    print("CRIOU A PlAYLIST")
    print(response.status_code)
    playlist_id = response.json()["id"]
    print(playlist_id)

    track_uris = []
    with open(Path(__file__).parent / "rec.csv", encoding="utf8") as csvfile:

        spamreader = csv.DictReader(csvfile)
        for row in spamreader:
            track_uris.append(row["uri"])

    print(track_uris)

    url_pl = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks".format(
        playlist_id=playlist_id
    )
    uris = dict()
    uris["uris"] = track_uris
    response = requests.post(url=url_pl, json=uris, headers=headers)
    print("Add Tracks ", response.status_code)
    return {"playlist_id": playlist_id, "tracks": len(track_uris), "status": response.status_code}
