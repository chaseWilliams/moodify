from flask import Flask, redirect, request
import requests as http
import json
import uuid
import numpy as np
import pandas as pd
import pprint
import csv
from lib.spotify import Spotify
from lib.learn import agglomerate_data
from lib.playlist import Playlist

user = Spotify('BQDt9jV8I3k1-5rIRzpKZgPcqQ2Cv4ZOt4mNz4_yfLZphti7u9TcCEC1OtNSSWy4YRctO3cPBTgT2AELd8O3AZ9ufNdWqcrZmE6e5IJC-7wuiOpqXpSNyCa4Fu3cjjyRe53wIhrmYIqz-Iyuua7Jiz8QtCkNUsK0JANbWNLVDTDuV1OVfb_I0zqVG4cLejc')
user.to_csv()
df = agglomerate_data(pd.read_csv('./data.csv'), 15)
playlist = Playlist(df, 15)

#for songs in playlist.playlists:
#    for x in range(0, 3):
        #print('| ' + songs[x]['track_name'] + ' | ')
    #print(len(songs))
    #print("\n---\n")

for x in range(0, 15):
    name = 'Moodify #' + str(x + 1)
    user.save_playlist(playlist.playlists[x], name)