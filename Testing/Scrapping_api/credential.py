import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
from datetime import datetime
import json
from auxiliar import getArtistStats

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

artist_table = dict()
artist_table["artists"] = []

try:
    while True:
        name = input("Artist Name = ")
        results = spotify.search(q="artist:" + name, type="artist", limit=5)

        for artist in results["artists"]["items"]:
            artist_data = getArtistStats(artist)
            if artist_data is not None:
                artist_table["artists"].append(artist_data)

except KeyboardInterrupt:
    path = f'./artists/artist_table_{datetime.now().strftime("%d")}_{datetime.now().strftime("%m")}_{datetime.now().strftime("%Y")}_at_{datetime.now().strftime("%H")}h_{datetime.now().strftime("%M")}m.json'
    with open(path, "w", encoding="utf-8") as f:
        json.dump(artist_table, f, ensure_ascii=False, indent=4)

    print("")
    print("Session Stopped")
