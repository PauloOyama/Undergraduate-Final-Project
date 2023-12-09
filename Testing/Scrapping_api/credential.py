import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
from datetime import datetime
import json


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def getArtistStats(artists: dict) -> dict | None:
    row = dict()

    if artists["popularity"] == 0:
        return None

    row["external_urls"] = artists["external_urls"]
    row["num_followers"] = artists["followers"]["total"]
    row["genres"] = artists["genres"]
    row["name"] = artists["name"]
    row["popularity"] = artists["popularity"]

    return row


artist_table = dict()
artist_table["artists"] = []

try:
    while True:
        name = input("Artist Name=")
        results = spotify.search(q="artist:" + name, type="artist", limit=5)

        for artist in results["artists"]["items"]:
            arg = getArtistStats(artist)
            if arg is not None:
                artist_table["artists"].append(arg)
                


except KeyboardInterrupt:
    path = f'./artists/artist_table_{datetime.now().strftime("%d")}_{datetime.now().strftime("%m")}_{datetime.now().strftime("%Y")}_at_{datetime.now().strftime("%H")}h_{datetime.now().strftime("%M")}m.json'
    with open(path, "w", encoding="utf-8") as f:
        json.dump(artist_table, f, ensure_ascii=False, indent=4)

    print("")
    print("BYE")
