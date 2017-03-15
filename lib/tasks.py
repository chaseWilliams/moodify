import redis as rd
from lib.spotify import User
from celery import Celery
import pickle

background_manager = Celery('tasks', broker='redis://localhost:6379/0')
redis = rd.StrictRedis(host='localhost', port=6379, db=0)

@background_manager.task
def create_user(token, lastfm):
    user = User(redis=redis, token=token, lastfm_name=lastfm)
    binary = pickle.dumps(user)
    redis.set(user.uid + '-obj', binary)
