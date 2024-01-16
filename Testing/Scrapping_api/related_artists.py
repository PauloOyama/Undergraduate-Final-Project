import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
from datetime import datetime
import time


def getRelatedArtists(artist_ids: List[str]):
    return spotify.artist_related_artists(artist_id=artist_ids)


def getArtistStats(artists: dict) -> dict | None:
    row = dict()

    if artists["popularity"] == 0:
        return None

    row["artist_id"] = artists["id"]
    row["external_urls"] = artists["external_urls"]
    row["num_followers"] = artists["followers"]["total"]
    row["genres"] = artists["genres"]
    row["name"] = artists["name"]
    row["popularity"] = artists["popularity"]

    return row


# folder path
dir_path = "./artists"

# list to store files
jsonFiles = []


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if path.startswith("ROK_"):
        continue
    if os.path.isfile(os.path.join(dir_path, path)):
        jsonFiles.append(os.path.join(dir_path, path))


top_track_table = dict()
top_track_table["artists"] = []
print(jsonFiles)
try:
    for file in jsonFiles:
        if len(jsonFiles) == 0:
            break
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

            artist_ids = []
            for related_artist in data["artists"]:
                res = getRelatedArtists(artist_ids=related_artist["artist_id"])
                if res is not None:
                    for artist in res["artists"]:
                        ls = getArtistStats(artist)
                        if ls is not None:
                            top_track_table["artists"].append(ls)

            # print(artist)
            if len(artist_ids) != 0:
                res = getRelatedArtists(artist_ids=artist_ids)
                print(res)
                if res is not None:
                    for artist in res["artists"]:
                        ls = getArtistStats(artist)
                        if ls is not None:
                            top_track_table["artists"].append(ls)
                artist_ids.clear()
            print(top_track_table["artists"])

        new_name = "OK_" + file.split("/")[2]
        os.rename(file, os.path.join(dir_path, new_name))

except Exception as err:
    print("Deu Ruim ", err)
finally:
    path = f'./all_artists/related_artists_{datetime.now().strftime("%d")}_{datetime.now().strftime("%m")}_{datetime.now().strftime("%Y")}_at_{datetime.now().strftime("%H")}h_{datetime.now().strftime("%M")}m.json'
    with open(path, "w", encoding="utf-8") as f:
        json.dump(top_track_table, f, ensure_ascii=False, indent=4)
