from flask import Flask, Response, redirect, request, url_for, render_template, after_this_request, g, make_response
import requests as http
import redis as rd
import json
import uuid
import numpy as np
from sklearn.mixture import GMM
import pandas as pd
import pprint
import os
from lib.spotify import User
from lib.tasks import create_user
from lib.curator import filter_with, BadFilter
from pusher import Pusher
import pickle

app = Flask(__name__)
client_id = 'c23563670ff943438fdc616383e9f0ea'
client_secret = '08e420d130d94312a20123663db0ec25'
ip = os.environ.get('IP', '127.0.0.1')
port = os.environ.get('PORT', '5000')
if ip == '0.0.0.0' and port == '8080':
    redirect_uri = 'http://moodify-dev-dude0faw3.c9users.io/callback'
else:
    redirect_uri = 'http://{0}:{1}/callback'.format(ip, port)
authorize_uri = 'https://accounts.spotify.com/authorize'
token_uri = 'https://accounts.spotify.com/api/token'
code = ''
redis = rd.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/loading')
def loading():
    uid = request.args.get('uid')
    token = redis.get(uid).decode('utf-8')
    lastfm = redis.get(uid + '-lastfm').decode('utf-8')
    print(token, lastfm)
    print(type(token), type(lastfm))
    create_user.delay(token, lastfm)
    return render_template('loading.html', uid=uid)

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
    api_me = 'https://api.spotify.com/v1/me'
    uid = http.get(api_me, headers={'Authorization': 'Bearer ' + token}).json()['id']
    redis.set(uid, token)
    check_token = redis.get(uid).decode('utf-8')
    print(token, check_token)
    print(token == check_token)
    return render_template('callback.html', uid=uid)

@app.route('/retrieve')
def retrieve():
    uid = request.args.get('uid')
    playlists = request.args.get('playlists')
    playlists = playlists.split(',')
    arr = []
    for playlist in playlists:
        key = uid + '-' + str(playlist)
        result = redis.get(key).decode('utf-8')
        arr.append(json.loads(result))
    string = json.dumps({'status': 'ok', 'contents': arr})
    response = make_response(string)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/save', methods=['POST'])
def save():
    content = request.get_json()
    uid = content['uid']
    identifier = content['identifier']
    playlist_name = content['name']
    playlist = redis.get(uid + '-' + identifier).decode('utf-8')
    playlist = pd.read_json(playlist, orient='split')
    generic_user = User(redis, uid=uid)
    generic_user.save_playlist(playlist, playlist_name)
    return 'awesome'

@app.route('/lastfm', methods=['POST'])
def save_lastfm():
    content = request.get_json()
    lastfm = content['lastfm']
    uid = content['uid']
    key, value = json.dumps(uid + '-lastfm'), json.dumps(lastfm)
    redis.set(key, value)
    return 'saved'

@app.route('/create', methods=['POST'])
def create():
    content = request.get_json()
    filters = content['filters']
    uid = content['uid']
    pprint.pprint(filters)
    user_binary = redis.get(uid + '-obj')
    user = pickle.loads(user_binary)
    try:
        new_playlist = filter_with(user, filters)
    except BadFilter:
        return_data = {
            'playlist': [],
            'identifier': '',
            'success': False,
            'message': 'History data nonexistent'
        }
        response = make_response(json.dumps(return_data))
        response.headers['Content-Type'] = 'application/json'
        return response
    playlist_json = new_playlist.to_json(orient='split')
    # create a unique identifier for the playlist
    identifier = str(uuid.uuid4())
    key = uid + '-' + identifier
    redis.set(key, playlist_json)
    track_names = list(new_playlist['track_name'].values)
    print(json.dumps(track_names))
    return_data = {
        'playlist': json.dumps(track_names),
        'identifier': identifier,
        'success': True,
        'message': 'Successfully created'
    }
    response = make_response(json.dumps(return_data))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/begin')
def begin():
    return app.send_static_file('index.html')

@app.route('/final')
def final():
    uid = request.args.get('uid')
    return render_template('final.html', uid=uid)

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
    app.run(
        host = ip,
        port = port,
        debug=True,
        use_reloader=True
    )
