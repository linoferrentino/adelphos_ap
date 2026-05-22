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

from app.transport.AbstractGateway import AbstractGateway
from app.ap_api.AsyncRequest import AsyncGetReq
from app.ap_api.AsyncRequest import AsyncPostReq
import aiohttp
import asyncio
from app.logging import gCon


class AsyncGateway(AbstractGateway):


    def __init__(self):
        try:
            loop = asyncio.get_running_loop() 
            self.loop = loop
        except RuntimeError:
            raise Exception("Async Gateway must be used with a running loop")
        self.requests = list()


    async def _dequeue_requests_or_wait_lock(self, session):
        while (len(self.requests) != 0):
            req = self.requests.pop()
            asyncio.create_task(req.async_req(session))
        await self.app.cond.wait()


    async def start(self, app):
        self.app = app
        self.ses_worker = asyncio.create_task(self.session_worker(app))


    async def stop(self):
        async with self.app.cond:
            self.app.cond.notify_all()
        await self.ses_worker


    async def session_worker(self, app):
        headers_acc = {"Accept" : "application/activity+json"}

        async with aiohttp.ClientSession(headers = headers_acc) as session:
            while app.running == True:
                async with app.cond:
                    await self._dequeue_requests_or_wait_lock(session)


    async def async_req_push(self, ar):
        async with self.app.cond:
            self.requests.append(ar)
            self.app.cond.notify_all()


    async def async_req_wait(self, ar):
        # I have to put it into the list and wait
        await self.async_req_push(ar)
        while (ar.status_code is None):
            async with ar._cond:
                await ar._cond.wait()
        if ar.status_code != 200:
            raise Exception(f"Got {ar.status_code} from {ar._url}")
        return ar.text


    async def route_message(self, method, urlp, json = None):

        if method == "GET":

            ar = AsyncGetReq(None)
            ar.init_split(urlp)
            return await self.async_req_wait(ar)

        elif method == "POST":
            post_res  = AsyncPostReq(inbox_uri, headers, json)
            assert False
        else:
            raise Exception(f"Invalid method {method}")


