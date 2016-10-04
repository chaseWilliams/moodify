from flask import Flask, redirect, request
import requests as http
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

@app.route("/callback")
def callback():
    code = request.args.get('code')
    result = http.post(token_uri, data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    })
    print('token result')
    print(result.json())
    dict = result.json()
    uid = uuid.uuid4()
    redis.set(str(uid), dict['access_token'])
    return "we did it! your token is " + dict['access_token']

@app.route('/retrieve')
def retrieve():
    uid = request.args.get('uid')
    token = redis.get(uid)
    user = Spotify(token)
    df = agglomerate_data(user.get_songs(), 8)
    data = Playlist(df)

@app.route("/authenticate")
def authenticate():
    return redirect(authorize_uri + '?client_id=' + client_id + \
                    '&response_type=code&redirect_uri=' + redirect_uri + '&scope=user-library-read')


if __name__ == "__main__":
    redis = redis.StrictRedis(host='localhost', port=6379, db=0)
    app.run()