import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
import pandas as pd
import json
from datetime import datetime


dir_path = "./track_features"
jsonFiles = []


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if path.startswith("OK_"):
        continue
    if os.path.isfile(os.path.join(dir_path, path)):
        jsonFiles.append(os.path.join(dir_path, path))


metadados = []

try:
    for file in jsonFiles:
        if len(jsonFiles) == 0:
            break

        # with open(file, "r", encoding="utf-8") as f:
        #     data = json.load(f)

        df = pd.read_json(file)
        print(df["audio_features"])

    # print(type(metadados))

    # path = f'./json_csv/metadados_csv_{datetime.now().strftime("%d")}_{datetime.now().strftime("%m")}_{datetime.now().strftime("%Y")}_at_{datetime.now().strftime("%H")}h_{datetime.now().strftime("%M")}m.csv'
    # df = pd.read_json(str(metadados))
    # df.to_csv(path)


except Exception as err:
    print("Deu Ruim: ", err)
# finally:
# with open(path, "w", encoding="utf-8") as f:
#     json.dump(metadados, f, ensure_ascii=False, indent=4)
