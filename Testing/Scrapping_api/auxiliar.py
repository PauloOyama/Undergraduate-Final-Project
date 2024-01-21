from typing import List
import os


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


def filterAudioFeatures(track_features: List) -> List[dict]:
    feat_tracks = []
    for feat in track_features:
        if feat is None:
            continue
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


def filesToRead(directory: str) -> List[str]:
    jsonFiles = []

    for path in os.listdir(directory):
        if path.startswith("OK_"):
            continue
        if os.path.isfile(os.path.join(directory, path)):
            jsonFiles.append(os.path.join(directory, path))

    return jsonFiles
