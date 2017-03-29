from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado import ioloop
import logging
logging.basicConfig(filename="debug.log", level=logging.INFO)

class Count:
    def __init__(self):
        self.count = 0
    def inc(self):
        self.count += 1
    def dec(self):
        self.count -= 1

def async_batch_requests(uris, response_func, callback, timeout, **kwargs):
    logger = logging.getLogger('batch')
    left_to_process = 0
    http_client = AsyncHTTPClient()
    count = Count()

    def response_wrapper(response):
        response_func(response, **kwargs)
        count.dec()
        if count.count == 0:
            ioloop.IOLoop.instance().stop()
            callback(**kwargs)
            
    for uri in uris:
        req = HTTPRequest(uri, request_timeout=timeout, connect_timeout=timeout)
        count.inc()
        http_client.fetch(req, callback=response_wrapper)
    ioloop.IOLoop.instance().start()