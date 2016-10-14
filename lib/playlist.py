import pandas as pd
import numpy as np
import random
import pprint

class Playlist:

    # songs is a pandas.DataFrame of all the songs
    # track_name, track_id, and all metadata minus cluster label
    def __init__(self, clustered_songs, num_playlists):
        self.songs = clustered_songs
        self.length = num_playlists
        #self.total_songs =
        #self._substantiate()

    # returns a portion_number-length list of songs for the playlist
    # as to represent the entire playlist
    def get_portion(self, portion_number=5):
        arr = []
        while len(arr) < portion_number:
            arr.append(self._random_song())
        return arr

    # adds additional details for the songs:
    # - Spotify href
    # - Track demo listen
    def _substantiate(self):
        return None

    # separate the songs according to their songs
    def separate(self):
        arr = []
        for id in range(0, self.length):
            sub_arr = []
            for song in self.songs.iterrows():
                song = song[1].to_dict()
                song_id = song['cluster_id']
                if song_id == id:
                    sub_arr.append(song)
            arr.append(sub_arr)
        return arr

    # returns a random song
    def _random_song(self):
        index = random.randrange(self.total_songs)
        return self.songs.iloc[index, :].values.tolist()

