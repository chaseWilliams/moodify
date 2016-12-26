import requests as http
import numpy as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
data = http.get('http://ws.audioscrobbler.com/2.0/?format=json&method=user.getrecenttracks&limit=200&api_key=b333a19b2c0397e8e4c1224b49b3e7cd&user=dude0faw3').json()
track_data = data['recenttracks']['track']
limit = data['recenttracks']['@attr']['totalPages']
page = 1
song_names = []
for track in track_data:
    song_names.append(track['name'])
print('Starting!')
while data['recenttracks']['@attr']['page'] != limit:
    page += 1
    print('...page ' + str(page))
    data = http.get('http://ws.audioscrobbler.com/2.0/?format=json&method=user.getrecenttracks&limit=200&api_key=b333a19b2c0397e8e4c1224b49b3e7cd&user=dude0faw3&page=' + str(page)).json()
    for track in data['recenttracks']['track']:
        song_names.append(track['name'])

print(Counter(song_names).most_common(100))