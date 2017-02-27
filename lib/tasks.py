from flask import Flask, Response, redirect, request, url_for, render_template, after_this_request, g
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
from pusher import Pusher
from celery import Celery

background_manager = Celery('tasks', broker='redis://localhost:6379/0')
client_id = 'c23563670ff943438fdc616383e9f0ea'
client_secret = '08e420d130d94312a20123663db0ec25'
redirect_uri = 'http://127.0.0.1:5000/callback'
authorize_uri = 'https://accounts.spotify.com/authorize'
token_uri = 'https://accounts.spotify.com/api/token'
code = ''
redis = rd.StrictRedis(host='localhost', port=6379, db=0)
num_playlists = 40
received_features = ['danceability', 'energy', 'acousticness', 'valence', 'tempo']

@background_manager.task
def create_user(token):
    user = User(received_features, num_playlists, redis=redis, token=token)
    for index, playlist in enumerate(user.playlists):
        key = user.uid + '-' + str(index)
        redis.set(key, json.dumps(playlist))
