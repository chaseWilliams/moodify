
import numpy as np
import requests as http
import pprint
import matplotlib.pyplot as plt
import pandas as pd
import csv
import json
import redis as rd
import re
from lib.lastfm import Lastfm
import pusher
import logging
logging.basicConfig(filename="debug.log", level=logging.INFO)

""" User is a class that effectively abstracts the HTTP requests to the Spotify API
and Last.fm API. It holds all of the user's information, but is not intended to
persist, but rather has options for exporting to a pandas DataFrame or csv file


Optional metadata includes:
 - danceability
 - energy
 - acousticness
 - valence
 - tempo

 Standard metadata includes:
 - name
 - id
 - popularity
 - genre
 - artist
"""

class User:
    ## Spotify API URL's
    api_base = 'https://api.spotify.com/v1'
    api_library_tracks = api_base + '/me/tracks' # only returns 50 songs at a time
    api_artists = api_base + '/artists'
    api_track_metadata = api_base + '/audio-features' # note -> max of 100 ids
    api_me = api_base + '/me'

    def __init__(self, redis=None, token=None, lastfm_name='dude0faw3'):
        if redis is None:
            redis = rd.StrictRedis(host='localhost', port=6379, db=0)
        if token is not None:
            self.library = pd.DataFrame()
            self.token = token
            self.songs = {}
            self.song_metadata = np.ndarray([])
            self.total_tracks = 0
            self.artists = []
            self.lastfm_name = lastfm_name
            self.lastfm = None # placeholder
            self.uid = self._get_user_id()
            self.pusher_client = pusher.Pusher(
                app_id='298964',
                key='33726bd9f5b34f01cc85',
                secret='391150c34b190fc05dc4',
                ssl=True
            )
            self.pusher_channel = 'user_instantiate_{0}'.format(self.uid)
            self.library_callback_stack = [
                self._base_metadata,
                self._handle_lastfm,
                self._assign_genres,
                self._optional_metadata,
                self._update_pusher
            ]
            self.build_library_messages = [
                'Downloading your library and basic metadata',
                'Connecting your library with additional Last.fm data',
                'Assigning genres to your songs',
                'Fetching final metadata points to create your user'
            ]
            self.progress = 0
            self.logger = logging.getLogger('logger')
            self._build_library()

            # url is user specific

            self.api_create_playlist = self.api_base + '/users/' + self.uid + '/playlists'
        else:
            token = redis.get(uid).decode('utf-8')
            self.token = token
            self.uid = uid
            self.api_create_playlist = self.api_base + '/users/' + self.uid + '/playlists'

    # saves the specified playlist
    def save_playlist(self, playlist, name):
        data = {
            'name': name
        }
        response = self._post(self.api_create_playlist, data)
        response = response.json()
        playlist_uri = response['href'] + '/tracks'
        uris = []
        for count, song in enumerate(playlist.itertuples()):
            if count == 100:
                dictionary = {'uris': uris}
                self._post(playlist_uri, dictionary)
                uris = []
            uris.append('spotify:track:' + song.track_id)
        if len(uris) > 0:
            dictionary = {'uris': uris}
            self._post(playlist_uri, dictionary)

    # handles all outgoing http requests
    def _get(self, endpoint, spotify=True):
        if spotify:
            request = http.get(endpoint, headers={'Authorization': 'Bearer ' + self.token})
        return request

    def _post(self, endpoint, data):
        request = http.post(endpoint, data=json.dumps(data), headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        return request

    def _get_user_id(self):
        print(self._get(self.api_me).text)
        return self._get(self.api_me).json()['id']

    # cyclic method that acts as a callback:
    # when it gets called again, it will perform the next function
    # semi-recursive nature
    def _build_library(self):
        next_func = self.library_callback_stack.pop(0)
        self._update_pusher()
        next_func()
        
    # get history data
    def _handle_lastfm(self):
        self.logger.info('lastfm')
        if self.lastfm_name != '':
            self.lastfm = Lastfm(name=self.lastfm_name, spotify=self.library, callback=self._get_count)
        else:
            self.lastfm = Lastfm()
            arr = [np.nan] * len(self.library)
            self.library['count'] = pd.Series(arr)
            self._build_library()

    # callback from initializing lastfm obj in handle_lastfm 
    # finishes the job of lastfm-related history metadata
    def _get_count(self):
        self.library['count'] = self.lastfm.get_count(self.library)
        self._build_library()

    def _base_metadata(self):
        self.logger.info('base')
        # get the first track object to determine total number of tracks in library
        response = self._get(self.api_library_tracks + '?limit=1')
        response = response.json()
        total_tracks = response['total']

        # go ahead and add first song
        temp_arr = []
        self._push_to_library(temp_arr, response['items'][0]['track'])

        # loop through and substantiate library of user

        for offset in list(range(1, total_tracks, 50)):
            batch = self._get(self.api_library_tracks + '?limit=50&offset=' + str(offset))
            batch_json = batch.json()
            for track in batch_json['items']:
                self._push_to_library(temp_arr, track['track'])

        self.total_tracks = len(temp_arr)
        self.library = pd.DataFrame(temp_arr)
        self.library.columns = ['track_name', 'track_id', 'artists', 'popularity', 'name', 'id']
        self._build_library()

    def _push_to_library(self, arr, track_object):
        metadata = [track_object.get(key) for key in ['name', 'id', 'popularity']]
        artists = [artist['name'] for artist in track_object['artists']]
        artists = ','.join(artists)
        for artist in track_object['artists']:
            name = artist['name']
            if name not in self.artists:
                self.artists.append(name)
        metadata.insert(2, artists)
        album_metadata = [track_object['album']['name'], track_object['album']['id']]
        metadata.extend(album_metadata)
        arr.append(metadata)

    # store all of the songs' metadata in a NumPy matrix, where index number is the same
    # as Spotify.user_songs
    def _optional_metadata(self):
        self.logger.info('optional')
        arr = []
        for offset in list(range(0, self.total_tracks, 100)):
            string = ''
            if offset + 100 > self.total_tracks:
                limit = offset + self.total_tracks - offset
            else:
                limit = offset + 100
            for index in list(range(offset, limit, 1)):
                name = self.library['track_id'][index]
                string += name + ','
            string = string.rstrip(',')
            url = self.api_track_metadata + '?ids=' + string
            result = self._get(url)
            result = result.json()['audio_features']
            for track in result:
                arr.append([
                    track['danceability'],
                    track['energy'],
                    track['acousticness'],
                    track['valence'],
                    track['tempo']
                ])
        df = pd.DataFrame(arr)
        df.columns = ['danceability', 'energy', 'acousticness', 'valence', 'tempo']
        self.library = pd.concat([self.library, df], axis=1)
        self._build_library()


    def _assign_genres(self):
        self.logger.info('genres')
        def callback(artist_genres):
            find_all_genres = np.vectorize(map_genres)
            genres = find_all_genres(self.library['artists'])
            self.library['genres'] = pd.Series(genres)
   
        artist_genres = self.lastfm.get_genres(self.artists, callback)
        self._build_library()

    def map_genres(track_artists):
        artists = track_artists.split(',')
        track_genres = []
        for artist in artists:
            # may not find the artist, that's ok
            try:
                track_genres.extend(artist_genres[artist])
            except KeyError:
                pass
        string = ''
        for genre in track_genres:
            if genre is not None:
                string += genre
            string += ','

        return string.rstrip(',')

    def _update_pusher(self):
        step_size = 1 / len(self.library_callback_stack)
        self.progress += 1
        if self.progress is len(self.library_callback_stack):
            data = {
                'progress': 100,
                'message': 'All done!'
            }
        else:
            progress = self.progress * step_size
            message = self.build_library_messages[self.progress - 1]
            data = {
                'progress': progress,
                'message': message
            }
        self.pusher_client.trigger(self.pusher_channel, 'update', data)
