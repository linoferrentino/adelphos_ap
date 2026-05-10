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
from starlette.applications import Starlette
from app.transport.async_mode.AsyncTransport import AsyncTransport
from starlette.types import Receive, Scope, Send
from app.consts import API_POINT
from app.logging import gCon


class StarletteWrap(Starlette):


    def __init__(self, routable, lifespan = None, root_path = API_POINT):
        transport = AsyncTransport()
        routable.set_transport(transport)
        routes = routable.get_routes()

        super().__init__(routes = routes, lifespan = lifespan)

        self.transport = transport
        self.running = False
        self.cond = asyncio.Condition()  
        self.in_gw = routable

        self.root_path = root_path


    # taken from FastApi code, file 
    # https://github.com/fastapi/fastapi/blob/master/fastapi/applications.py
    # I did not want to use all FastApi, just Starlette, but I needed the
    # root_path capability
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.root_path:
            scope["root_path"] = self.root_path
        await super().__call__(scope, receive, send)


    def get_config(self):
        return self.in_gw.config


    def set_out_gateway(self, gw):
        self.transport.set_gateway(gw)

