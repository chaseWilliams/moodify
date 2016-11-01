from flask import Flask, redirect, request
import requests as http
import redis as rd
import json
import uuid
import numpy as np
from sklearn.mixture import GMM
import pandas as pd
import pprint
import csv
from lib.spotify import Spotify
from lib.learn import agglomerate_data
from lib.playlist import Playlist

app = Flask(__name__)
client_id = 'c23563670ff943438fdc616383e9f0ea'
client_secret = '08e420d130d94312a20123663db0ec25'
redirect_uri = 'http://127.0.0.1:5000/callback'
authorize_uri = 'https://accounts.spotify.com/authorize'
token_uri = 'https://accounts.spotify.com/api/token'
code = ''
redis = None

@app.route('/callback')
def callback():
    code = request.args.get('code')
    response = http.post(token_uri, data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    })
    response = response.json()
    token = response['access_token']
    user = Spotify(token)
    for index, playlist in enumerate(user.playlists):
        key = user.uid + '-' + str(index)
        redis.set(key, json.dumps(playlist))
        name = 'Moodify #' + str(index + 1)
        user.save_playlist(playlist, name)
    string = "we did it! your token is " + token
    return string + "\n\n" + json.dumps(user.playlists)

@app.route('/retrieve')
def retrieve():
    uid = request.args.get('uid')
    playlists = request.args.get('playlists')
    print(uid)
    playlists = playlists.split(',')
    arr = []
    for index, playlist in enumerate(playlists):
        key = uid + '-' + str(index)
        result = redis.get(key).decode('utf-8')
        arr.append(json.loads(result))
    string = json.dumps({'status': 'ok', 'contents': arr})
    response = Flask.make_response(string)
    response.headers['Content-Type'] = 'application/json'
    return response

#@app.route('/save')
#def save():


@app.route('/authenticate')
def authenticate():
    return redirect(authorize_uri + '?client_id=' + client_id + \
                    '&response_type=code&redirect_uri=' + redirect_uri + '&scope=user-library-read playlist-modify-public')


if __name__ == "__main__":
    redis = rd.StrictRedis(host='localhost', port=6379, db=0)
    app.run()