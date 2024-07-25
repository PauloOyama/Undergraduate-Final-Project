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

from spotipy.oauth2 import SpotifyClientCredentials


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def getMusicFeatures(ids: List):
    return spotify.audio_features(tracks=ids)


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):

    url = "https://api.spotify.com/v1/me/top/tracks"
    print("Auth=" + q)
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
def read_item(item_id: int, q: Union[str, None] = None):

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
    with open("./rec.csv", encoding="utf8") as csvfile:

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
    return {"item_id": item_id, "q": q}
