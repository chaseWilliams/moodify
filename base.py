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

user = Spotify('BQD4sX7BcTdVlLRu7xPkVn3hrNnOj4U-lDw4NBLoU7QW71pbQZJFNE3YhLnrQao50QB1z7RIZQZiZgOI_sgzItxe2Ko21mCAM9NoYyo-ebOaWBVWwWgLJar6C-dszXwE43XL2eyIeKg18oo2VHopIiPTfDVZjZGjkzlEQr5Obwohfd4-1RTpn2YXUvZ3O0xM1OdJ')
user.save_playlist(playlist.playlists[0])