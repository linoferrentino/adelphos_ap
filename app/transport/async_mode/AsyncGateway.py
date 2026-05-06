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
     
        gCon.log(f"req len {len(self.requests)}") 
        while (len(self.requests) != 0):
            req = self.requests.pop()
            asyncio.create_task(req.async_req(session))
        await self.app.cond.wait()


    async def start(self, app):
        gCon.log("Starting the gateway")
        self.app = app
        self.ses_worker = asyncio.create_task(self.session_worker(app))


    async def stop(self):
        await self.ses_worker


    async def session_worker(self, app):
        headers_acc = {"Accept" : "application/activity+json"}

        async with aiohttp.ClientSession(headers = headers_acc) as session:
            while app.running == True:
                async with app.cond:
                    gCon.log("something?")
                    await self._dequeue_requests_or_wait_lock(session)


    async def async_req_push(self, ar):
        async with self.app.cond:
            self.requests.append(ar)
            gCon.log("append, now I notify")
            self.app.cond.notify_all()


    async def async_req_wait(self, ar):
        # I have to put it into the list and wait
        await self.async_req_push(ar)
        gCon.log(f"async req to {ar._url} posted, now I wait")
        while (ar.status_code is None):
            async with ar._cond:
                await ar._cond.wait()
        gCon.log(f"got result {ar.status_code} in client request!")
        return ar.status_code


    async def route_message(self, method, urlp, json = None):

        if method == "GET":

            ar = AsyncGetReq(None)
            ar.init_split(urlp)
            return await self.async_req_wait(ar)

        elif method == "POST":
            assert False
        else:
            raise Exception(f"Invalid method {method}")


