from tornado.httpclient import AsyncHTTPClient, HTTPRequest

class Count:
    def __init__(self):
        self.count = 0
    def inc(self):
        self.count += 1
    def dec(self):
        self.count -= 1

def async_batch_requests(uris, response_func, callback, timeout, **kwargs):
    left_to_process = 0
    http_client = AsyncHTTPClient()
    count = Count()

    def response_wrapper(response):
        response_func(response, **kwargs)
        count.dec()
        if count.count == 0:
            callback(**kwargs)
            
    for uri in uris:
        req = HTTPRequest(uri, request_timeout=timeout)
        count.inc()
        http_client.fetch(req, response_wrapper)