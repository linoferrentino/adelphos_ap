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

from tests.transport.sync_mode.loop import run_coro_in_loop, get_loop
from app.logging import gCon


class WebSocketSync(ContextDecorator):


    def __enter__(self):
        return self


    def __exit__(self, *exc):
        return False


    def __init__(self, pair_sock = None):
        gCon.log(f"[red]{id(self)}[/red] init pair {pair_sock}")
        if pair_sock is None:
            self.is_server = False
            self.pair_sock = None
        else:
            self.is_server = True
            self.cond = asyncio.Condition()
            self.pair_sock = pair_sock
        self.buffer = None


    #async def client_serving_loop(self):
    #    assert self.is_server == False
    #    while True:
    #        gCon.log(f"xxxxxx client serving loop! {id(self)} server {self.is_server}")
    #        text = await self.receive_text()
    #        gCon.log(f"ZZZZZZ client serving loop! {id(self)} server {self.is_server}")


    #async def accept_sync(self):
    #    gCon.log(f"accepting sync {self.pair_sock}")
    #    while self.pair_sock is None:
    #        async with self.cond:
    #            gCon.log(f"accepting sync wait")
    #            await self.cond.wait()


    async def sending_text_async(self, text):
        gCon.log(f"--> sending {text} from {id(self)}, pair buffer {self.pair_sock.buffer} server {self.is_server}")

        if self.is_server == False:
            cond = self.pair_sock.cond
        else:
            cond = self.cond

        async with cond:
            self.pair_sock.buffer = text
            cond.notify_all()


    async def accept(self):
        assert self.is_server
        #wss = WebSocketSync(self)
        #self.pair_sock = wss
        gCon.log(f"[red]{id(self)}[/red] accept is_server {self.is_server}")
        #asyncio.create_task(WebSocketSync.client_serving_loop(self.pair_sock))
        #async with self.cond:
        #    self.cond.notify_all()
        #return wss


    def send_text(self, text: str) -> None:
        gCon.log(f"[red]{id(self)}[/red] send_text /{text}/ is server {self.is_server}")

        #run_coro_in_loop(self.sending_text_async, text, False)
        run_coro_in_loop(self.sending_text_async, text, True)
        #if self.is_server:
        #else:
        #    run_coro_in_loop(WebSocketSync.sending_text_async_client, text)


    def receive_text(self) -> str:

        gCon.log(f"[red]{id(self)}[/red] receive_text {self.buffer} server {self.is_server}")
        text = run_coro_in_loop(self.receive_text_blocking_async, self)
        gCon.log(f"[red]{id(self)}[/red] temp RECEIVE {text}")
        #if isinstance(text, asyncio.Task) == True:
        #    gCon.log("Waiting result")
        #    try:
        #        get_loop().run_until_complete(text)
        #        text = text.result()
        #    except Exception as ex:
        #        gCon.log(f"HELP {ex}")
        #        raise ex
        #    gCon.log("OOOOO")

        gCon.log(f"FINAL RECEIVE {text}")
        #if self.is_server:
        #else:
        #    text = run_coro_in_loop(self.receive_text_blocking_async, self)
        return text


    async def receive_text_blocking_async(self, stub = None):

        if self.is_server == False:
            cond = self.pair_sock.cond
        else:
            cond = self.cond
        
        data = None 
        gCon.log(f"[red]{id(self)}[/red] receive async buffer /{self.buffer}/")
        async with cond:
            while self.buffer is None:
                gCon.log(f"[red]{id(self)}[/red], server {self.is_server}, I wait to receive")
                await cond.wait()
                gCon.log(f"[red]{id(self)}[/red], exited from cond {data}")

            data = self.buffer
            self.buffer = None

        gCon.log(f"[red]{id(self)}[/red] has received {data}")
        return data 


class SyncTester:


    def __init__(self, app):
        self.app = app


    def _check_path(self, path):

        urls = urlsplit(path)
        if len(urls.scheme) != 0:
            raise Exception(f"I did not expect a scheme {urls.scheme}")
        if len(urls.netloc) != 0:
            raise Exception("I did not expect a location")
        return urls


    def websocket_connect(self, path) -> WebSocketSync:
        sock = WebSocketSync()
        gCon.log(f"web socket start {sock}")
        self.app.incoming_websocket(path, sock)
        gCon.log(f"END------ web socket now is {sock}")
        return sock


    def post(self, path, json):
        urlparse = self._check_path(path)
        #if (isinstance(path, str)):
        #    urlparse = self._check_path(path)
        #elif (isinstance(path, int)):
        #    urlparse = path
        #else:
        #    raise Exception(f"type {path} not expected got {type(path)}")
        return self.app.in_post_json(urlparse, json)
        

    def get(self, path):
        urlparse = self._check_path(path)
        return self.app.in_get_json(urlparse)

