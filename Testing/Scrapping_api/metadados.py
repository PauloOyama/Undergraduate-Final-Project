import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
from datetime import datetime


def getMusicFeatures(ids: List):
    return spotify.audio_features(tracks=ids)


def filterAudioFeatures(track_features: List):
    feat_tracks = []
    for feat in track_features:
        res = dict()

        res["danceability"] = feat["danceability"]
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

        feat_tracks.append(res)

    return feat_tracks


dir_path = "./top_tracks_f"
jsonFiles = []


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if path.startswith("OK_"):
        continue
    if os.path.isfile(os.path.join(dir_path, path)):
        jsonFiles.append(os.path.join(dir_path, path))


metadados = dict()
metadados["audio_features"] = []

try:
    for file in jsonFiles:
        if len(jsonFiles) == 0:
            break

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

            count = 1

            track_ids = []
            for artist in data["top_tracks"]:
                print(artist["track_id"], count)
                track_ids.append(artist["track_id"])
                if count % 100 == 0:
                    res = getMusicFeatures(ids=track_ids)
                    if res is not None:
                        # print(res)
                        filtered_audios = filterAudioFeatures(res)
                        print(filtered_audios)
                        metadados["audio_features"] = (
                            metadados["audio_features"] + filtered_audios
                        )
                    track_ids.clear()

                count += 1

            if len(track_ids) != 0:
                res = getMusicFeatures(ids=track_ids)
                if res is not None:
                    print(res)
                    filtered_audios = filterAudioFeatures(res)
                    print(filtered_audios)
                    metadados["audio_features"] = (
                        metadados["audio_features"] + filtered_audios
                    )

                track_ids.clear()

        new_name = "OK_" + file.split("/")[2]
        os.rename(file, os.path.join(dir_path, new_name))

except Exception as err:
    print("Deu Ruim: ", err)
finally:
    path = f'./track_features/metadados_table_{datetime.now().strftime("%d")}_{datetime.now().strftime("%m")}_{datetime.now().strftime("%Y")}_at_{datetime.now().strftime("%H")}h_{datetime.now().strftime("%M")}m.json'
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadados, f, ensure_ascii=False, indent=4)
