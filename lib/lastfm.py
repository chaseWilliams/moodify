import requests as http
import re
from lib.timemachine import TimeMachine
import pandas as pd
import numpy as np
import unicodedata
from collections import Counter
from lib.batch import async_batch_requests
import json

class Lastfm:

    ## Last.fm API URL's
    last_key = 'b333a19b2c0397e8e4c1224b49b3e7cd'
    last_genre_method = 'artist.gettopTags'
    last_history_method = 'user.getrecenttracks'
    last_base = 'http://ws.audioscrobbler.com/2.0/?method={0}&api_key={1}&format=json'
    last_genre_url = last_base.format(last_genre_method, last_key) + '&autocorrect=1&artist='
    last_history_url = last_base.format(last_history_method, last_key) + '&limit=200&user='

    def __init__(self, name=None, spotify=None, callback=None):
        if name is not None:
            self.name = name
            self.spotify = spotify
            self.get_history(callback)
            
    def get_genres(self, artists, callback):
        urls = []
        genres = {}
        url_map = {}
        for artist in artists:
            url = self.last_genre_url + artist
            url = url.replace(' ', '+')
            urls.append(url)
            url_map[url] = artist
        def req_callback(**kwargs):
            callback(genres)
        async_batch_requests(urls, self.handle_response, req_callback, 200, genres=genres, url_map=url_map)
        
    def handle_response(response, genres, url_map):
        artist = url_map[response.effective_url]
        if response.error:
            print("Error:", response.error, response.effective_url)
        else:
            try:
                res_json = json.loads(response.body.decode('utf-8'))
                tags = res_json['toptags']['tag']
                genres[artist] = [
                    self.normalize_tags(tags, 0),
                    self.normalize_tags(tags, 1)
                ]
            except KeyError:
                genres[artist] = [None, None]

    def normalize_tags(self, tags, index):
        try:
            string = tags[index]['name']
            result = re.findall(r'([A-z])', string)
            return ''.join(result).lower()
        except IndexError:
            return None

    def get_history(self, callback):
        # make initial call
        url = self.last_history_url + self.name
        data = http.get(url).json()

        track_data = data['recenttracks']['track']
        limit = data['recenttracks']['@attr']['totalPages']
        page = 1
        history = []
        
        for track in track_data:
            history.append(self._check_track(track))

        uris = []
        for x in range(1, int(limit) + 1):
            uri = url + '&page=' + str(x)
            uris.append(uri)
        
        def req_callback(response, history):
            if response.error:
                print("Error:", response.error, response.effective_url)
            else:
                data = json.loads(response.body.decode('utf-8'))
                for track in data['recenttracks']['track']:
                    history.append(self._check_track(track))

        def final_callback(history):
            history_df = pd.DataFrame(history)
            history_df.columns = ['track_name', 'artists', 'date']
            self.history_df = history_df
            self.refine_df(self.spotify, callback)

        async_batch_requests(uris, req_callback, final_callback, 200, history=history)

    # determine the n-most frequently played songs from a given pandas series
    def determine_frequencies(self, data, num_songs, neglected=False):
        if neglected:
            counter = Counter(data)
            frequencies = counter.most_common()
            index = len(frequencies) - num_songs
            return frequencies[ index :]
        else:
            counter = Counter(data)
            return counter.most_common(num_songs)

    # clean lastfm data to only have songs currently in spotify library
    def refine_df(self, spotify, callback):
        must_haves = spotify['track_name']
        def check(val):
            for must_have in must_haves:
                if must_have.lower() == val.lower():
                    return True
            return False
        arr_check = np.vectorize(check)
        self.history_df = self.history_df[ arr_check(self.history_df[ 'track_name' ]) ]
        callback(self.history_df)

    def occurences_in_history(self, track_name, track_artists, timeslice=None):
        count = 0
        if timeslice is not None:
            year = timeslice[0]
            season = timeslice[1]
            machine = TimeMachine(year)
            if season == 'all':
                history = machine.in_year(self.history_df)
            else:
                history = machine.in_season(season, self.history_df)
        else:
            history = self.history_df
        track_artists = track_artists.split(',')
        for track, history_artist in zip(history['track_name'].values, history['artists'].values):
            # ignore potential formatting differences
            if track.lower() == track_name.lower():
                for artist in track_artists:
                    if self.strip_accents(artist.lower()) == self.strip_accents(history_artist.lower()):
                        count += 1
        return count
    # timeslice should be a tuple of year, season (or 'all')
    def get_count(self, spotify, timeslice=None):
        count_arr = [None] * len(spotify)
        for row in spotify.itertuples():
            count = self.occurences_in_history(row.track_name, row.artists, timeslice)
            count_arr[row.Index] = count
        return pd.Series(count_arr)

    def strip_accents(self, text):
        try:
            text = unicode(text, 'utf-8')
        except NameError: # unicode is a default on python 3 
            pass
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        return str(text)

    def _check_track(self, track):
            arr = [track.get('name', FakeNone()),
            track.get('artist', FakeNone()).get('#text', FakeNone()),
            track.get('date', FakeNone()).get('uts', FakeNone())
            ]
            return [None if type(x) == FakeNone else x for x in arr]

class FakeNone:
    def get(*args):
        return FakeNone()