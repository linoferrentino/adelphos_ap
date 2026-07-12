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

import asyncio

from urllib.parse import urlsplit
from contextlib import ContextDecorator
from contextlib import ExitStack 

from app.transport.bridge.loop import run_coro_in_loop, get_loop, is_in_loop
from app.logging import gCon
from starlette.websockets import WebSocketDisconnect


class WebSocketSync(ContextDecorator):


    def __enter__(self):

        return self


    def __exit__(self, *exc):

        return False


    def __init__(self, pair_sock = None):

        if pair_sock is None:
            self.is_server = False
            self.pair_sock = None
        else:
            self.is_server = True
            self.cond = asyncio.Condition()
            self.pair_sock = pair_sock
        self.buffer = None
        self.closed = False


    def get_cond(self):
        if self.is_server == False:
            cond = self.pair_sock.cond
        else:
            cond = self.cond
        return cond


    async def sending_text_async(self, text):
        cond = self.get_cond()

        async with cond:

            if self.closed == True:
                raise WebSocketDisconnect()

            self.pair_sock.buffer = text
            cond.notify_all()


    async def accept(self):

        assert self.is_server


    def send_text(self, text: str) -> None:
        is_loop = is_in_loop()
        if is_loop == True:
            return self.sending_text_async(text)
        return run_coro_in_loop(self.sending_text_async, (text,), wait = True)


    def receive_text(self) -> str:
        text = run_coro_in_loop(self.receive_text_blocking_async, ())
        return text


    def close(self):
        run_coro_in_loop(self.close_async, (), wait = False)


    async def close_async(self):
        cond = self.get_cond()
        async with cond:
            self.closed = True
            cond.notify_all()


    async def receive_text_blocking_async(self):

        cond = self.get_cond()

        data = None 
        async with cond:
            while self.buffer is None:
                await cond.wait()

            if self.closed == True:
                raise WebSocketDisconnect()

            data = self.buffer
            self.buffer = None

        return data 


class SyncTester(ContextDecorator):


    def __init__(self, app):
        self.app = app


    def __enter__(self):
        self.app.on_startup()
        return self


    def __exit__(self, *exc):
        self.app.on_teardown()
        return False


    def _check_path(self, path):

        urls = urlsplit(path)
        if len(urls.scheme) != 0:
            raise Exception(f"I did not expect a scheme {urls.scheme}")
        if len(urls.netloc) != 0:
            raise Exception("I did not expect a location")
        return urls


    def get_routable(self):
        return self.app


    def get_kernel(self):
        return self.app.get_kernel()


    def websocket_connect(self, path) -> WebSocketSync:
        sock = WebSocketSync()
        self.app.incoming_websocket(path, sock)
        return sock


    def post(self, path, json, headers = {}):
        urlparse = self._check_path(path)
        return self.app.in_post_json(urlparse, json, headers)
        

    def get(self, path):
        urlparse = self._check_path(path)
        return self.app.in_get_json(urlparse)

