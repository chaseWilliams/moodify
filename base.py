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

df = agglomerate_data(pd.read_csv('./lib/data.csv'), 15)
playlist = Playlist(df, 15)

#for songs in playlist.playlists:
#    for x in range(0, 3):
        #print('| ' + songs[x]['track_name'] + ' | ')
    #print(len(songs))
    #print("\n---\n")

user = Spotify('BQAUy-uiBODTHJiMotQ9TYbxCb2NUfNyIgMcYypjeUJdfJIVE5QcnhJppS_J37gKTDi3x1vq-7xxu6bQYw7eOaL_CnhAtYQ3tK2P1DZIgugyc4d459yFS2Bpx0wY5XtlBtePWfjbsRPLOf_TN9li3m_8Cc62t42b')
print(playlist.playlists[0])
user.save_playlist(playlist.playlists[0])