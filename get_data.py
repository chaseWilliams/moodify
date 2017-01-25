
# Note: user must exist in the redis instance
import numpy as np
import requests as http
import pandas as pd
import csv
import json
import redis as rd
from lib.spotify import User

def gmm_playlists_to_csv(uid):
    features = [
        'track_id',
        'track_name',
        'popularity',
        'cluster_id',
        'danceability',
        'energy',
        'acousticness',
        'valence',
        'tempo'
    ]
    nums = ','.join(str(x) for x in range(40))
    api_url = 'http://127.0.0.1:5000/retrieve?uid=' + uid + '&playlists=' + nums
    data = []
    result = http.get(api_url)
    result = result.json()['contents']
    for playlist in result:
        for track in playlist:
            metadata = []
            for key in features:
                if key in track.keys():
                    metadata.append(track[key])
            data.append(metadata)
    with open('data.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['track_id', 'track_name', 'popularity', 'playlist_id', 'danceability', 'energy', 'acousticness', 'valence', 'tempo'])
        for row in data:
            writer.writerow(row)
    return 'data.csv updated for the user ' + uid
