import requests as http
import re
from lib.timemachine import TimeMachine
import pandas as pd
import numpy as np
import unicodedata
from collections import Counter


class Lastfm:

    ## Last.fm API URL's
    last_key = 'b333a19b2c0397e8e4c1224b49b3e7cd'
    last_genre_method = 'artist.gettopTags'
    last_history_method = 'user.getrecenttracks'
    last_base = 'http://ws.audioscrobbler.com/2.0/?method={0}&api_key={1}&format=json'
    last_genre_url = last_base.format(last_genre_method, last_key) + '&autocorrect=1&artist='
    last_history_url = last_base.format(last_history_method, last_key) + '&limit=200&user='

    def __init__(self, name=None, spotify=None, pusher=None):
        if name is not None:
            self.name = name
            self.pusher_client = pusher['obj']
            self.pusher_start = pusher['start']
            self.pusher_change = pusher['change']
            self.pusher_channel = pusher['channel']
            self.get_history()
            self.refine_df(spotify)


    def get_genres(self, artists, start, change, pusher_client, pusher_channel):
        count = 0
        cap = len(artists)
        def normalize_tags(tags, index):
            try:
                string = tags[index]['name']
                result = re.findall(r'([A-z])', string)
                return ''.join(result).lower()
            except IndexError:
                return None
        genres = {}
        for artist in artists:
            data = {
                'message': 'Getting Last.fm information about {0}...'.format(artist),
                'progress': start + change * (count / cap) 
            }
            pusher_client.trigger(pusher_channel, 'update', data)
            count += 1
            url = self.last_genre_url + artist
            response = http.get(url).json()
            try:
                tags = response['toptags']['tag']
                genres[artist] = [
                    normalize_tags(tags, 0),
                    normalize_tags(tags, 1)
                ]
            except KeyError:
                genres[artist] = [None, None]
                
        return genres

    def get_history(self,):
        # make initial call
        url = self.last_history_url + self.name
        data = http.get(url).json()

        track_data = data['recenttracks']['track']
        limit = data['recenttracks']['@attr']['totalPages']
        page = 1
        history = []

        for track in track_data:
            history.append(self._check_track(track))
            
        while int(data['recenttracks']['@attr']['page']) is not int(limit):
            progress = page / int(limit)
            progress_bar_location = self.pusher_change * progress + self.pusher_start
            pusher_data = {
                'message': 'On page {0} out of {1} pages of your history'.format(page, limit),
                'progress': progress_bar_location
            }
            self.pusher_client.trigger(self.pusher_channel, 'update', pusher_data)
            page += 1
            data = http.get(url + '&page=' + str(page)).json()
            for track in data['recenttracks']['track']:
                history.append(self._check_track(track))
        
        history_df = pd.DataFrame(history)
        history_df.columns = ['track_name', 'artists', 'date']
        self.history_df = history_df
        return history_df

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
    def refine_df(self, spotify):
        must_haves = spotify['track_name']
        def check(val):
            for must_have in must_haves:
                if must_have.lower() == val.lower():
                    return True
            return False
        arr_check = np.vectorize(check)
        return spotify[ arr_check(spotify[ 'track_name' ]) ]

    def occurences_in_history(self, track_name, track_artists, timeslice=None):
        count = 0
        if timeslice is not None:
            year = timeslice[0]
            season = timeslice[1]
            machine = TimeMachine(year)
            if season is None:
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
    # timeslice should be a tuple of year(, season)
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