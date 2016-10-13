
import numpy as np
import requests as http
import pprint
import matplotlib.pyplot as plt
import pandas as pd
import csv
import json

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

    def __init__(self, token):
        self.token = token
        self.songs = {}
        self.artists = {}
        self.song_metadata = np.ndarray([])
        self.total_tracks = 0
        self._build_library()
        # url is user specific
        uid = self._get_user_id()
        print(uid)
        self.api_create_playlist = self.api_base + '/users/' + uid + '/playlists'


    # returns a panda.DataFrame of all present genres in user's library
    def get_genres(self):
        return None

    # returns a panda.DataFrame of all the artists present in user's library
    def get_artists(self):
        return None

    # returns a panda.DataFrame of the artists' songs
    def get_songs(self):
        arr = []
        for sample in self.songs:
            arr.append([sample, self.songs[sample]])
        df = pd.DataFrame(arr)
        df.columns = ['track_name', 'track_id']
        return df

    # returns all of the user's songs' attributes in an panda.DataFrame
    def get_song_metadata(self):
        array = self._metadata()
        df = pd.DataFrame(array)
        df.columns = ['Danceability', 'Energy', 'Acousticness', 'Valence', 'Tempo']
        return df

    # saves the specified playlist
    def save_playlist(self, playlist, name):
        data = {
            'name': name
        }
        response = self._post(self.api_create_playlist, data)
        response = response.json()
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(response)
        #playlist_id = response['items'][0]['id']
        playlist_uri = response['href'] + '/tracks'
        uris = []
        for song in playlist:
            uris.append('spotify:track:' + song['track_id'])
        dictionary = {'uris': uris}
        result = self._post(playlist_uri, dictionary)
        print(result)
        result = result.json()
        print(result)


    # only handles songs right now, needs to handle artists and song metadata as well
    def to_csv(self):
        arr = []
        for index, row in self.get_songs().iterrows():
            arr.append(row)
        arr = np.asarray(arr)
        result = np.hstack((arr, self.get_song_metadata().values))
        with open('data.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['track_name', 'track_id', 'Danceability', 'Energy', 'Acousticness', 'Valence', 'Tempo'])
            for row in result:
                writer.writerow(row)

    # handles all outgoing http requests
    def _get(self, endpoint):
        request = http.get(endpoint, headers={'Authorization': 'Bearer ' + self.token})
        return request

    def _post(self, endpoint, data):
        request = http.post(endpoint, data=json.dumps(data), headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        return request

    def _get_user_id(self):
        response = self._get(self.api_me).json()['id']
        print(response)
        return response

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
            self.artists[artist['name']] = artist['id']

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

#user = Spotify('BQCPgPFZ6X0zydhljGcGZhXHUffhxONoNNJvRq81BK78kMgc8sA2FKm2o_qwpnNPRvgjsCzYbjbI0-brjuiHr0AW3-3yuKCe4Jq-2JDKb_P6SOEbyECmCxUQQIhlEUcTtME7BreUBZIiGdE0iO0_Hl5Baw4DK9qS')
#user.to_csv()
#print(user.get_song_metadata())