
import numpy as np
import requests as http
import pprint
import matplotlib.pyplot as plt
import pandas as pd
import csv
import json
import redis as rd
from lib.playlist import Playlist
from lib.learn import agglomerate_data

""" Spotify is a class that effectively abstracts the HTTP requests to the Spotify API

An individual Spotify object that can act as a direct representation of a user's Spotify

Song metadata includes:
 - danceability
 - energy
 - acousticness
 - valence
 - tempo
"""

class Spotify:
    api_base = 'https://api.spotify.com/v1'
    api_library_tracks = api_base + '/me/tracks' # only returns 50 songs at a time
    api_artists = api_base + '/artists'
    api_track_metadata = api_base + '/audio-features' # note -> max of 100 ids
    api_me = api_base + '/me'

    def __init__(self, chosen_features=None, num_playlists=None, redis=None, token=None, uid=None):
        if redis is None:
            redis = rd.StrictRedis(host='localhost', port=6379, db=0)
        if token is not None:
            self.token = token
            self.songs = {}
            self.artist_ids = []
            self.song_metadata = np.ndarray([])
            self.total_tracks = 0
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


    # takes a list of artist ids and returns a comma separated string of all genres (repeats)
    def get_genres(self, ids):
        artist_ids = np.array(ids)
        ceiling = len(artist_ids)
        all_genres = ''
        for offset in list(range(0, ceiling, 50)):
            string = ''
            if offset + 50 > ceiling:
                limit = ceiling
            else:
                limit = offset + 50
            for index in list(range(offset, limit, 1)):
                string += artist_ids[index] + ','
            string = string.rstrip(',')
            response = self._get(self.api_artists + '?ids=' + string)
            response = response.json()
            for artist in response['artists']:
                genres = ','.join(artist['genres'])
                all_genres += genres + ','
        all_genres = all_genres.rstrip(',')
        return all_genres

    # returns a python list of the artists' songs
    def get_songs(self):
        arr = []
        for sample in self.songs:
            arr.append([sample, self.songs[sample]])
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
        df.columns = ['track_name', 'track_id', 'danceability', 'energy', 'acousticness', 'valence', 'tempo']
        return df

    # handles all outgoing http requests
    def _get(self, endpoint):
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

    def _push_to_library(self, track_object):
        self.songs[track_object['name']] = track_object['id']
        for artist in track_object['artists']:
            self.artist_ids.append(artist['id'])

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
                string += self.songs[name] + ','
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

    def _get_single_genre(self, id):
        uri = self.api_artists + '/' + id
        response = self._get(uri)
        response = response.json()
        # return comma-separated str of the genres
        return ','.join(response['genres'])
