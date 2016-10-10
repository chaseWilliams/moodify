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

df = agglomerate_data(pd.read_csv('./lib/data.csv'), 20)
playlist = Playlist(df, 20)

for dictionary in playlist.playlists[3]:
    print('| ' + dictionary['track_name'] + ' | ')