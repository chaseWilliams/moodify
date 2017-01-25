import requests as http
import re


class Lastfm:

    ## Last.fm API URL's
    last_key = 'b333a19b2c0397e8e4c1224b49b3e7cd'
    last_genre_method = 'artist.gettopTags'
    last_base = 'http://ws.audioscrobbler.com/2.0/?method={0}&api_key={1}&format=json'
    last_genre_url = last_base.format(last_genre_method, last_key) + '&autocorrect=1&artist='

    def __init__(self, name=None):
        self.name = name

    def get_genres(self, artists):
        def normalize_tags(tags, index):
            try:
                string = tags[index]['name']
                result = re.findall(r'([A-z])', string)
                return ''.join(result).lower()
            except IndexError:
                return None
        genres = {}
        for artist in artists:
            url = self.last_genre_url + artist
            response = http.get(url).json()
            try:
                tags = response['toptags']['tag']
                genres[artist] = [
                    normalize_tags(tags, 0),
                    normalize_tags(tags, 1)
                ]
            except KeyError:
                print(artist)
                genres[artist] = [None, None]
        return genres

    ##def get_history():
