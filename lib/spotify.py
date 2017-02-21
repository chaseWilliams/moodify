
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
from lib.lastfm import Lastfm
import pusher

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
 - artist
"""

class User:
    ## Spotify API URL's
    api_base = 'https://api.spotify.com/v1'
    api_library_tracks = api_base + '/me/tracks' # only returns 50 songs at a time
    api_artists = api_base + '/artists'
    api_track_metadata = api_base + '/audio-features' # note -> max of 100 ids
    api_me = api_base + '/me'

    def __init__(self, chosen_features=None, num_playlists=None, redis=None, token=None, uid=None, lastfm=None):
        if redis is None:
            redis = rd.StrictRedis(host='localhost', port=6379, db=0)
        if token is not None:
            self.library = pd.DataFrame()
            self.token = token
            self.songs = {}
            self.song_metadata = np.ndarray([])
            self.total_tracks = 0
            self.artists = []
            self.uid = self._get_user_id()
            self.pusher_client = pusher.Pusher(
                app_id='298964',
                key='33726bd9f5b34f01cc85',
                secret='391150c34b190fc05dc4',
                ssl=True
            )
            self.pusher_channel = 'user_instantiate_{0}'.format(self.uid)
            self._build_library()

            # url is user specific

            self.api_create_playlist = self.api_base + '/users/' + self.uid + '/playlists'
            labeled_songs = agglomerate_data(self.library, num_playlists, chosen_features)
            self.playlists = Playlist(labeled_songs, num_playlists).separate()
            redis.set(self.uid, self.token)
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
        for song in playlist:
            uris.append('spotify:track:' + song['track_id'])
        dictionary = {'uris': uris}
        result = self._post(playlist_uri, dictionary)
        result = result.json()

    # handles all outgoing http requests
    def _get(self, endpoint, spotify=True):
        if spotify:
            request = http.get(endpoint, headers={'Authorization': 'Bearer ' + self.token})
        return request

    def _post(self, endpoint, data):
        request = http.post(endpoint, data=json.dumps(data), headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        return request

    def _get_user_id(self):
        return self._get(self.api_me).json()['id']

    def _build_library(self):
        # build up base library metadata
        change = 1 / 3 * 100
        data = {
            'message': 'Grabbing basic metadata about your library...',
            'progress': 0
        }
        self._update_pusher(data)
        self._base_metadata(0, change)

        # add the genres
        data['progress'] = change
        data['message'] = 'Getting Last.fm information about your user...'
        self._update_pusher(data)
        self._assign_genres(change, change)

        # add the optional metadata
        data['progress'] = change * 2
        data['message'] = 'Acquiring final metadata for each song in your library...'
        self._update_pusher(data)
        self._optional_metadata(change * 2, change)

        data['progress'] = 100
        data['message'] = 'Finished!'
        self._update_pusher(data)
    def _base_metadata(self, start, change):
        # get the first track object to determine total number of tracks in library
        response = self._get(self.api_library_tracks + '?limit=1')
        response = response.json()
        total_tracks = response['total']

        # go ahead and add first song
        temp_arr = []
        self._push_to_library(temp_arr, response['items'][0]['track'])

        # loop through and substantiate library of user

        for offset in list(range(1, total_tracks, 50)):
            progress = offset / total_tracks
            progress_bar_location = change * progress + start
            data = {
                'message': 'Grabbing basic metadata about your library...',
                'progress': progress_bar_location
            }
            self._update_pusher(data)
            batch = self._get(self.api_library_tracks + '?limit=50&offset=' + str(offset))
            batch_json = batch.json()
            for track in batch_json['items']:
                self._push_to_library(temp_arr, track['track'])

        self.total_tracks = len(temp_arr)
        self.library = pd.DataFrame(temp_arr)
        self.library.columns = ['track_name', 'track_id', 'artists', 'popularity']

    def _push_to_library(self, arr, track_object):
        metadata = [track_object.get(key) for key in ['name', 'id', 'popularity']]
        artists = [artist['name'] for artist in track_object['artists']]
        artists = ','.join(artists)
        for artist in track_object['artists']:
            name = artist['name']
            if name not in self.artists:
                self.artists.append(name)
        metadata.insert(2, artists)
        arr.append(metadata)

    # store all of the songs' metadata in a NumPy matrix, where index number is the same
    # as Spotify.user_songs
    def _optional_metadata(self, start, change):
        arr = []
        for offset in list(range(0, self.total_tracks, 100)):
            data = {
                'message': 'Acquiring final metadata for each song in your library...',
                'progress': start + change * (offset / self.total_tracks)
            }
            self._update_pusher(data)
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


    def _assign_genres(self, start, change):
        lastfm = Lastfm()
        artist_genres = lastfm.get_genres(self.artists, start, change, self.pusher_client, self.pusher_channel)
        cap = len(self.library['artists'])
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

        find_all_genres = np.vectorize(map_genres)

        genres = find_all_genres(self.library['artists'])
        self.library['genres'] = pd.Series(genres)

    def _update_pusher(self, data):
        self.pusher_client.trigger(self.pusher_channel, 'update', data)
