import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
from datetime import datetime
from auxiliar import getArtistStats, filesToRead
import time


def getRelatedArtists(artist_ids: List[str]):
    return spotify.artist_related_artists(artist_id=artist_ids)


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

top_track_table = dict()
top_track_table["artists"] = []

jsonFiles = filesToRead("./artists")


try:
    for file in jsonFiles:
        if len(jsonFiles) == 0:
            break
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

            for related_artists in data["artists"]:
                list_related_artist = getRelatedArtists(
                    artist_ids=related_artists["artist_id"]
                )
                if list_related_artist is not None:
                    for artist in list_related_artist["artists"]:
                        artist_data = getArtistStats(artist)
                        if artist_data is not None:
                            top_track_table["artists"].append(artist_data)

        new_name = "OK_" + file.split("/")[2]
        os.rename(file, os.path.join("./artists", new_name))

except Exception as err:
    print("An error has occured", err)
finally:
    path = f'./artists/OK_related_artists_{datetime.now().strftime("%d")}_{datetime.now().strftime("%m")}_{datetime.now().strftime("%Y")}_at_{datetime.now().strftime("%H")}h_{datetime.now().strftime("%M")}m.json'
    with open(path, "w", encoding="utf-8") as f:
        json.dump(top_track_table, f, ensure_ascii=False, indent=4)
