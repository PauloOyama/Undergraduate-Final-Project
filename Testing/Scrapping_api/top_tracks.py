import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
from datetime import datetime
import time


def getArtistTopTracks(artist_id: str, market: str = "BR"):
    return spotify.artist_top_tracks(artist_id=artist_id, country=market)


def filterTopTrackStats(track: dict):
    res = dict()
    res["artist_id"] = track["artists"][0]["id"]
    res["track_id"] = track["id"]
    res["name"] = track["name"]
    res["track_popularity"] = track["popularity"]
    res["uri"] = track["uri"]

    return res


# folder path
dir_path = "./artists"

# list to store files
jsonFiles = []


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if path.startswith("OK_"):
        continue
    if os.path.isfile(os.path.join(dir_path, path)):
        jsonFiles.append(os.path.join(dir_path, path))


top_track_table = dict()
top_track_table["top_tracks"] = []

try:
    for file in jsonFiles:
        if len(jsonFiles) == 0:
            break
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

            count = 1
            for artist in data["artists"]:
                res = getArtistTopTracks(artist["artist_id"])
                if count % 30 == 0:
                    time.sleep(20)
                if res is not None:
                    for track in res["tracks"]:
                        top_track_table["top_tracks"].append(filterTopTrackStats(track))
                        print(track["name"])

                count += 1

        new_name = "OK_" + file.split("/")[2]
        os.rename(file, os.path.join(dir_path, new_name))

except Exception:
    print("Deu Ruim")
finally:
    path = f'./top_tracks_f/top_track_table_{datetime.now().strftime("%d")}_{datetime.now().strftime("%m")}_{datetime.now().strftime("%Y")}_at_{datetime.now().strftime("%H")}h_{datetime.now().strftime("%M")}m.json'
    with open(path, "w", encoding="utf-8") as f:
        json.dump(top_track_table, f, ensure_ascii=False, indent=4)
