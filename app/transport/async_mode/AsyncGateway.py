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


from app.transport.AbstractGateway import AbstractGateway
from app.ap_api.AsyncRequest import AsyncGetReq
from app.ap_api.AsyncRequest import AsyncPostReq
import aiohttp
import asyncio
import threading
from app.logging import gCon
from starlette.exceptions import HTTPException
from app.transport.bridge.loop import get_loop


class AsyncGateway(AbstractGateway):


    def __init__(self):
        try:
            #loop = asyncio.get_running_loop() 
            loop = get_loop()
            self.loop = loop
        except RuntimeError:
            raise Exception("Async Gateway must be used with a running loop")
        self.requests = list()


    async def _dequeue_requests_or_wait_lock(self, session):
        while (len(self.requests) != 0):
            req = self.requests.pop()
            asyncio.create_task(req.async_req(session))
        gCon.log(f"WAITING COND {self.app} on thread {threading.current_thread().native_id}")
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
        while (ar.status_code is None):
            async with ar._cond:
                await ar._cond.wait()


    async def async_req_post(self, ar):
        await self.async_req_push(ar)
        return ar.status_code


    async def async_req_wait(self, ar):
        # I have to put it into the list and wait
        await self.async_req_push(ar)
        if ar.status_code != 200:
            gCon.log(f"Got {ar.status_code} from {ar._url}")
            raise HTTPException(ar.status_code)
        #gCon.log(f"Got the text {ar.text}")
        return ar.text


    async def route_message(self, method, urlp, json = None, headers = {}):

        if method == "GET":

            ar = AsyncGetReq(None)
            ar.init_split(urlp)
            return await self.async_req_wait(ar)

        elif method == "POST":
            post_res  = AsyncPostReq(None, headers, json)
            post_res.init_split(urlp)
            gCon.log(f"Sending to {urlp} ------")
            return await self.async_req_post(post_res)
            #return 202
        else:
            raise Exception(f"Invalid method {method}")


