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

from app.transport.async_mode.AsyncGateway import AsyncGateway
from contextlib import asynccontextmanager
from starlette.applications import Starlette
from app.transport.async_mode.AsyncTransport import AsyncTransport
from starlette.types import Receive, Scope, Send
from starlette.responses import Response
from starlette.responses import PlainTextResponse

from app.consts import API_POINT
from app.logging import gCon

from app.exc.AdelphosException import AdelphosException 
from app.exc.AdelphosException import AdErrno

from starlette.middleware import Middleware
from app.sdc.Dependencies import Dependencies


class AdelphosExcMiddleware:

    def __init__(self, app):
        self.app = app


    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except AdelphosException as exc:
            response = PlainTextResponse(f"{exc.out_str}: {exc}",
                                         status_code = 401)
            await response(scope, receive, send)


@asynccontextmanager
async def async_lifespan_gw(app):

    app.running = True
    out_gateway = AsyncGateway()
    app.set_out_gateway(out_gateway)

    await out_gateway.start(app)
    await app.routable.init_up()

    yield

    app.running = False

    await app.routable.tear_down()
    await out_gateway.stop()


class StarletteWrap(Starlette):


    def __init__(self, routable, root_path = API_POINT):
        transport = AsyncTransport()
        routable.set_transport(transport)
        routes = routable.get_routes()

        middleware = [
                Middleware(AdelphosExcMiddleware),
                ]

        super().__init__(routes = routes, lifespan = async_lifespan_gw, 
                         middleware = middleware)

        self.transport = transport
        self.running = False
        self.cond = asyncio.Condition()  
        self.routable = routable

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
        return self.routable.conf()


    def set_out_gateway(self, gw):
        self.transport.set_gateway(gw)


    def get_routable(self):
        return self.routable

