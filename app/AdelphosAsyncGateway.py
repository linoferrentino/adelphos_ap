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

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.responses import PlainTextResponse
from contextlib import asynccontextmanager

from app.transport.AbstractTransport import AbstractTransport
from app.ap_api.ActivityPubMockup import ActivityPubMockup
from app.ap_api.ActivityPubMockup import ActivityPubMockupConfig

def aa_homepage(request):
    return PlainTextResponse('Hello, world!')


@asynccontextmanager
async def lifespan(app):
    print('Startup')
    yield
    print('Shutdown')


class AdelphosAsyncGateway(AbstractTransport):


    def homepage(request):
        return PlainTextResponse('Hello, world!')

    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

#
#routes = [
#        Route('/', AdelphosAsyncGateway.homepage),
#    ]
#

def ad_get_app(host):

    config = ActivityPubMockupConfig()

    mockup = ActivityPubMockup()

    ap_routes = mockup.get_async_routes()

    app = AdelphosAsyncGateway(routes=ap_routes, lifespan=lifespan)

    return app

