
import numpy as np
import requests as http
import pprint
import matplotlib.pyplot as plt
import pandas as pd
import csv

""" Spotify is a class that effectively abstracts the HTTP requests to the Spotify API

An individual Spotify object that can act as a direct representation of a user's Spotify

"""

class Spotify:
    api_base = 'https://api.spotify.com/v1'
    api_library_tracks = api_base + '/me/tracks' # only returns 50 songs at a time
    api_artists = api_base + '/artists'
    api_track_metadata = api_base + '/audio-features' # note -> max of 100 ids

    def __init__(self, token):
        self.token = token
        self.songs = {}
        self.artists = {}
        self.song_metadata = np.ndarray([])
        self._build_library()

    # returns a panda.DataFrame of all present genres in user's library
    def get_genres(self):
        return None

    # returns a panda.DataFrame of all the artists present in user's library
    def get_artists(self):
        return None

    # returns a panda.DataFrame of the artists' songs
    def get_songs(self):
        arr = []
        for sample in user.songs:
            arr.append([sample, user.songs[sample]])
        df = pd.DataFrame(arr)
        return df

    # returns all of the user's songs' attributes in an panda.DataFrame
    def get_song_metadata(self):
        return None

    # only handles songs right now, needs to handle artists and song metadata as well
    def to_csv(self):
        with open('data.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['track_name', 'track_id'])
            for index, row in self.get_songs().iterrows():
                writer.writerow(row.tolist())

    # builds the playlists for the user to check out
    def build_playlists(self):
        return None

    # returns a 7-song shortened version of the playlist
    def playlist_sample(self, playlist):
        return None

    # saves the identified playlist to the user's Spotify
    def save_playlist(self, playlist):
        return None

    # handles all outgoing http requests
    def _get(self, endpoint):
        request = http.get(endpoint, headers={'Authorization': 'Bearer ' + self.token})
        return request

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

    def _push_to_library(self, track_object):
        self.songs[track_object['name']] = track_object['id']
        for artist in track_object['artists']:
            self.artists[artist['name']] = artist['id']

    # store all of the songs' metadata in a NumPy matrix, where index number is the same
    # as Spotify.user_songs
    def _metadata(self):
        return None



user = Spotify('BQB6iyAQUqZRoV9577SKQxLV6zRXhDnTS_mQauIu6xhDuegjLuEqV6Z4Qw10uEpboulyV8H06xAPZhiq9B6z-JtnA-Z_1odFQnXQBSLPcGTtkYh-89lo1EU_tTOzLlBopq5yUUjzv-bItMiLmwm-li4OZaBSSprr')