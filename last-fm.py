import requests as http
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
data = http.get('http://ws.audioscrobbler.com/2.0/?format=json&method=user.getrecenttracks&limit=200&api_key=b333a19b2c0397e8e4c1224b49b3e7cd&user=dude0faw3').json()
track_data = data['recenttracks']['track']
limit = data['recenttracks']['@attr']['totalPages']
page = 1
history = []
# for nested dictionary entry requests
class FakeNone:
    def get(*args):
        return FakeNone()
# ensures that there's no key error exception
def add_track(track):
    arr = [track.get('name', FakeNone()),
     track.get('artist', FakeNone()).get('#text', FakeNone()),
      track.get('date', FakeNone()).get('uts', FakeNone())
    ]
    return [None if type(x) == FakeNone else x for x in arr]
for track in track_data:
    add_track(track)
print('Starting!')
while int(data['recenttracks']['@attr']['page']) is not limit:
    page += 1
    print('...page ' + str(page))
    data = http.get('http://ws.audioscrobbler.com/2.0/?format=json&method=user.getrecenttracks&limit=200&api_key=b333a19b2c0397e8e4c1224b49b3e7cd&user=dude0faw3&page=' + str(page)).json()
    for track in data['recenttracks']['track']:
        add_track(track)
df = pd.DataFrame(history)
print(df.tail())
