######################################################
#
# Adelphos AP: the fractal trust network
#
# Activity Pub implementation
#
# © 2025-26 Lino Ferrentino
# lino.ferrentino@gmail.com
#
# This is free software. Licensed with GPL version 3
#
######################################################
#
# this is the class that models an async request in adelphos

import asyncio
from abc import ABC, abstractmethod
from app.logging import gCon
from urllib.parse import urlsplit
import re


# the base class for all the requests in Adelphos.
# In adelphos we only use json payloads.
# And we use for now only GET and PUT
class AsyncRequestBase(ABC):

    # I can create an async request using a url and this will create a
    # condition.
    def __init__(self, url):

        u = urlsplit(url)

        if ((re.match('localhost', u.netloc)) or
            (re.match('127.0.0.1', u.netloc))):
            #gCon.log("Asking localhost, I change to http")
            new_u = u._replace(scheme = 'http')
            self._url = new_u.geturl()
        else:
            self._url = url


    @abstractmethod
    async def async_req(self, session):
        pass
    

class AsyncGetReq(AsyncRequestBase):


    def __init__(self, url):
        super().__init__(url)
        self._cond = asyncio.Condition()
        # I do not have (yet) a status code and a response
        self.status_code = None
        self.text = None


    async def async_req(self, session):
        try:
            await self.async_req_try(session)
        except Exception as ex:
            gCon.log(f"Exception while trying to get the URL {self._url}")
            # I put a generic user error
            self.status_code = 400
            self.text = str(ex)
        finally:
            # Ok, now I can signal the waiting task
            async with self._cond:
                self._cond.notify()


    async def async_req_try(self, session):
        #gCon.log(f"will request the url {self._url}")
        async with session.get(self._url) as resp:
            self.status_code = resp.status
            self.text = await resp.text()
        #gCon.log(f"got response {self.status_code} now I signal")


# this class posts the request with the signatures.
class AsyncPostReq(AsyncRequestBase):


    def __init__(self, url, headers, json):
        super().__init__(url)
        # the post response has a json payload 
        self._headers = headers
        self._json = json


    async def async_req(self, session):
        #gCon.log(f"will post to url {self._url}")
        async with session.post(self._url, headers = self._headers,
                                json = self._json):
            pass


