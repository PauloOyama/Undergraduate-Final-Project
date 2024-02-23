import os
import json
import spotipy
import time
from typing import List
from datetime import datetime
from auxiliar import filterAudioFeatures, filesToRead

from spotipy.oauth2 import SpotifyClientCredentials


def getMusicFeatures(ids: List):
    return spotify.audio_features(tracks=ids)


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

jsonFiles = filesToRead("./top_tracks_f")

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
            for track in data["top_tracks"]:
                print(track["track_id"], count)
                track_ids.append(track["track_id"])
                if count % 100 == 0:
                    res = getMusicFeatures(ids=track_ids)
                    if res is not None:
                        filtered_audios = filterAudioFeatures(res)
                        metadados["audio_features"] = (
                            metadados["audio_features"] + filtered_audios
                        )
                    track_ids.clear()
                    time.sleep(20)
                count += 1

            if len(track_ids) != 0:
                res = getMusicFeatures(ids=track_ids)
                if res is not None:
                    filtered_audios = filterAudioFeatures(res)
                    metadados["audio_features"] = (
                        metadados["audio_features"] + filtered_audios
                    )

                track_ids.clear()

        new_name = "OK_" + file.split("/")[2]
        os.rename(file, os.path.join("./top_tracks_f", new_name))

except Exception as err:
    print("An error has occured: ", err)
finally:
    path = f'./track_features/metadados_table_{datetime.now().strftime("%d")}_{datetime.now().strftime("%m")}_{datetime.now().strftime("%Y")}_at_{datetime.now().strftime("%H")}h_{datetime.now().strftime("%M")}m.json'
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadados, f, ensure_ascii=False, indent=4)
