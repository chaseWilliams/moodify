
import numpy as np
import requests as http
import pprint
import matplotlib.pyplot as plt
import pandas as pd
import csv
import json
import redis as rd
import re
from lib.playlist import Playlist
from lib.learn import agglomerate_data

""" Usr is a class that effectively abstracts the HTTP requests to the Spotify API
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
"""

class User:
    ## Spotify API URL's
    api_base = 'https://api.spotify.com/v1'
    api_library_tracks = api_base + '/me/tracks' # only returns 50 songs at a time
    api_artists = api_base + '/artists'
    api_track_metadata = api_base + '/audio-features' # note -> max of 100 ids
    api_me = api_base + '/me'

    ## Last.fm API URL's
    last_key = b333a19b2c0397e8e4c1224b49b3e7cd
    last_genre_method = 'artist.gettopTags'
    last_base = 'http://ws.audioscrobbler.com/2.0/?method={0}&api_key={1}&format=json'
    last_genre_url = last_base.format(last_genre_method, last_key) + '&autocorrect=1&artist='

    def __init__(self, chosen_features=None, num_playlists=None, redis=None, token=None, uid=None):
        if redis is None:
            redis = rd.StrictRedis(host='localhost', port=6379, db=0)
        if token is not None:
            self.token = token
            self.songs = {}
            self.song_metadata = np.ndarray([])
            self.total_tracks = 0
            self.artists = []
            self._build_library()
            # url is user specific
            self.uid = self._get_user_id()
            self.api_create_playlist = self.api_base + '/users/' + self.uid + '/playlists'
            labeled_songs = agglomerate_data(self.to_df(), num_playlists, chosen_features)
            self.playlists = Playlist(labeled_songs, num_playlists).separate()
            redis.set(self.uid, self.token)
        else:
            token = redis.get(uid).decode('utf-8')
            self.token = token
            self.uid = uid
            self.api_create_playlist = self.api_base + '/users/' + self.uid + '/playlists'

    # returns a python list of the artists' songs
    def get_songs(self):
        arr = []
        for sample in self.songs:
            arr.append([sample, *self.songs[sample]])
        arr = np.asarray(arr)
        result = np.hstack((arr, self.get_song_metadata().values))
        return result

    # returns all of the user's songs' attributes in an panda.DataFrame
    def get_song_metadata(self):
        array = self._metadata()
        df = pd.DataFrame(array)
        df.columns = ['danceability', 'energy', 'acousticness', 'valence', 'tempo']
        return df

    # saves the specified playlist
    def save_playlist(self, playlist, name):
        data = {
            'name': name
        }
        response = self._post(self.api_create_playlist, data)
        response = response.json()
        playlist_uri = response['href'] + '/tracks'
        uris = []
        for song in playlist:
            uris.append('spotify:track:' + song['track_id'])
        dictionary = {'uris': uris}
        result = self._post(playlist_uri, dictionary)
        print(result)
        result = result.json()
        print(result)

    # returns a panda DataFrame of all song data
    def to_df(self):
        arr = self.get_songs()
        df = pd.DataFrame(arr)
        df.columns = ['track_name', 'track_id', 'popularity', 'danceability', 'energy', 'acousticness', 'valence', 'tempo']
        print(df)
        return df

    # handles all outgoing http requests
    def _get(self, endpoint, spotify=True):
        if Spotify:
            request = http.get(endpoint, headers={'Authorization': 'Bearer ' + self.token})
        return request

    def _post(self, endpoint, data):
        request = http.post(endpoint, data=json.dumps(data), headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        return request

    def _get_user_id(self):
        return self._get(self.api_me).json()['id']

    def _build_library(self):
        # get the first track object to determine total number of tracks in library
        response = self._get(self.api_library_tracks + '?limit=1')
        response = response.json()
        total_tracks = response['total']

        # go ahead and add first song
        self._push_to_library(response['items'][0]['track'])

        # loop through and substantiate library of user
        for offset in list(range(1, total_tracks, 50)):
            batch = self._get(self.api_library_tracks + '?limit=50&offset=' + str(offset))
            batch_json = batch.json()
            for track in batch_json['items']:
                self._push_to_library(track['track'])
        self.total_tracks = len(self.songs)
        self._get_genres()

    def _push_to_library(self, track_object):
        self.songs[track_object['name']] = [track_object['id'], track_object['popularity']]
        for artist in track_object['artists']:
            name = artist['name']
            if name not in self.artists:
                self.artists.append(name)

    # store all of the songs' metadata in a NumPy matrix, where index number is the same
    # as Spotify.user_songs
    def _metadata(self):
        arr = []
        for offset in list(range(0, self.total_tracks, 100)):
            string = ''
            keys = list(self.songs.keys())
            if offset + 100 > self.total_tracks:
                limit = offset + self.total_tracks - offset
            else:
                limit = offset + 100
            for index in list(range(offset, limit, 1)):
                name = keys[index]
                string += self.songs[name][0] + ','
            string = string.rstrip(',')
            result = self._get(self.api_track_metadata + '?ids=' + string)
            result = result.json()['audio_features']
            for track in result:
                arr.append([
                    track['danceability'],
                    track['energy'],
                    track['acousticness'],
                    track['valence'],
                    track['tempo']
                ])
        return np.asarray(arr)

    def _get_genres():
        def normalize(string):
            result = re.findall(r'([A-z])', string)
            return ''.join(result).lower()
        print(self.artists)
        genres = []
        for artist in self.artists:
            print(artist)
            url = last_genre_url + artist
            response = http.get(url).json()
            tags = response['toptags']['tag']
            genres.append([
                normalize(tags[0]['name']),
                normalize(tags[1]['name'])
            ])
        
