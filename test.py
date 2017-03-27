import lib.lastfm as lastfm
from lib.batch import async_batch_requests
import logging

logger = logging.getLogger('test')
def callback(**kwargs):
    logger.info('yuh')
    
def resp(resp, **kwargs):
    logger.info('got it')
#usr = lastfm.Lastfm(name='dude0faw3', callback=callback)

uris = [
    'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key=b333a19b2c0397e8e4c1224b49b3e7cd&format=json&limit=200&user=dude0faw3&page=1',
    'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key=b333a19b2c0397e8e4c1224b49b3e7cd&format=json&limit=200&user=dude0faw3&page=169',
    'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key=b333a19b2c0397e8e4c1224b49b3e7cd&format=json&limit=200&user=dude0faw3&page=115'
]

async_batch_requests(uris, resp, callback, 200)
