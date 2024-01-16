import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
import glob
import pandas as pd
import json
from datetime import datetime
import csv


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

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        headers = data["audio_features"][0].keys()
        print(headers)

        path = f'./json_csv/metadados_csv_{datetime.now().strftime("%d")}_{datetime.now().strftime("%m")}_{datetime.now().strftime("%Y")}_at_{datetime.now().strftime("%H")}h_{datetime.now().strftime("%M")}m.csv'
        with open(path, "w") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data["audio_features"])

        new_name = "OK_" + file.split("/")[2]

        os.rename(file, os.path.join(dir_path, new_name))

    csv_files = glob.glob("./json_csv/*.{}".format("csv"))
    df_csv_concat = pd.concat(
        [pd.read_csv(file) for file in csv_files], ignore_index=True
    )
    df_csv_concat.to_csv("./json_csv/metadados_dataset.csv")


except Exception as err:
    print("Deu Ruim: ", err)
