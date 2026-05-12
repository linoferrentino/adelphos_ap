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

from contextlib import asynccontextmanager

from app.transport.async_mode.AsyncTransport import AsyncTransport
from app.transport.async_mode.StarletteWrap import StarletteWrap
from app.transport.async_mode.AsyncGateway import AsyncGateway

from app.logging import gCon


def starlette_app_creator(routable):
    app = StarletteWrap(routable = routable, lifespan = async_lifespan_gw)
    return app


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

 
