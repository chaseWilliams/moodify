from flask import Flask, Response, redirect, request, url_for, render_template, after_this_request
import requests as http
import redis as rd
import json
import uuid
import numpy as np
from sklearn.mixture import GMM
import pandas as pd
import pprint
import csv
from lib.spotify import User
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
num_playlists = 40
received_features = ['danceability', 'energy', 'acousticness', 'valence', 'tempo']

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
    user = User(received_features, num_playlists, redis=redis, token=token)
    print('USER -- ' + user.uid + " -- TOKEN IS:\n" + token + "\n")
    for index, playlist in enumerate(user.playlists):
        key = user.uid + '-' + str(index)
        redis.set(key, json.dumps(playlist))
    return render_template('callback.html', uid=user.uid)

@app.route('/retrieve')
def retrieve():
    uid = request.args.get('uid')
    playlists = request.args.get('playlists')
    print(uid)
    playlists = playlists.split(',')
    arr = []
    for playlist in playlists:
        key = uid + '-' + str(playlist)
        print(key)
        result = redis.get(key).decode('utf-8')
        arr.append(json.loads(result))
    string = json.dumps({'status': 'ok', 'contents': arr})

    @app.after_request
    def add_header(response):
        response.headers['Content-Type'] = 'application/json'
        return response
    return string

@app.route('/save', methods=['POST'])
def save():
    content = request.get_json()
    uid = content['uid']
    playlist_index = content['playlist']
    name = content['name']
    key = uid + '-' + str(playlist_index)
    playlist = redis.get(key).decode('utf-8')
    playlist = json.loads(playlist)
    user = User(redis, uid=uid)
    user.save_playlist(playlist, name)
    return 'awesome'

@app.route('/test')
def test():
    return app.send_static_file('callback.html')

@app.route('/begin')
def begin():
    return app.send_static_file('index.html')

@app.route('/authenticate')
def authenticate():
    return redirect(authorize_uri + '?client_id=' + client_id + \
                    '&response_type=code&redirect_uri=' + redirect_uri + '&scope=user-library-read playlist-modify-public')

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

if __name__ == "__main__":
    redis = rd.StrictRedis(host='localhost', port=6379, db=0)
    app.run()
