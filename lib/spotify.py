

""" Spotify is a class that effectively abstracts the HTTP requests to the Spotify API

An individual Spotify object can act as a direct representation of a user's Spotify,
or as a generic Spotify access point (without user-specific permissions)
"""
class Spotify:
    api_base = 'https://api.spotify.com/v1'
    api_library = api_base + '/me/tracks'
    api_artists = api_base + '/artists'

    def __init__(self, token):
        self.token = token

    # returns the count of all present genres in user's library
    def genres(self):

    # returns the count of all the artists present in user's library
    def artists(self):

    # returns a list of the artists' songs
    def songs(self):

    # returns all of the user's songs' attributes in an panda dataframe

    def song_metadata(self):
