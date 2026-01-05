# this is the class that models an async request in adelphos

import asyncio


class AsyncRequest:

    # I can create an async request using a url and this will create a
    # condition.
    def __init__(self, url, method = "get", headers = None, json = None):

        self._url = url
        self._method = method 
        self._headers = headers
        self._cond = asyncio.Condition()
        self._json = json
        self.status_code = None


