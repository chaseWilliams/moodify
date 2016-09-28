import pandas as pd
import numpy as np
import random

class Playlist:

    # songs is a pandas.DataFrame of all the songs
    # track_name, track_id, and all metadata minus cluster label
    def __init__(self, songs):
        self.songs = songs
        self.total_songs = len(songs.index)
        self._substantiate()

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

    # returns a random song
    def _random_song(self):
        index = random.randrange(self.total_songs)
        return self.songs.iloc[index, :].values.tolist()

