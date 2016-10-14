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

user = Spotify(' BQCkWP9_zxXQaTmyo-uOVk5bWfHmQ4u5ooHoRInMD2RUmZrJUqwi5N_ek7U0HCZvjbRMBXUdSlJYIIfQfs2-gFE_l7jIhReLRricMZqhCeCCYRsdkCTBlHuNA3NcoBmEsc_6mzgoXDdxjrdTPx8tIZIxIWjTWj2_6DtttTo2zfKgqSz-CPvYsP1bBBTzNKghw1VSKte4uq2c')
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(user.playlists.separate())

#for songs in playlist.playlists:
#    for x in range(0, 3):
        #print('| ' + songs[x]['track_name'] + ' | ')
    #print(len(songs))
    #print("\n---\n")

for x in range(0, 15):
    name = 'Moodify #' + str(x + 1)
    #user.save_playlist(playlist.playlists[x], name)