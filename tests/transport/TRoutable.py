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

from app.transport.Routable import Routable
from starlette.routing import Route
from starlette.responses import PlainTextResponse
from starlette.responses import Response
from starlette.responses import JSONResponse

from app.logging import gCon

from contextlib import asynccontextmanager

from app.transport.async_mode.AsyncGateway import AsyncGateway
import json

HOST_1 = "www.host1.org"
HOST_2 = "www.host2.org"

FLAG_1 = "XXXzzz"
FLAG_1_NEW = "XXXZZZ"

FLAG_2 = "XXXyyy"
FLAG_2_NEW = "XXXYYY"



class TRoutable(Routable):


    def __init__(self, transport, flag):
        self.transport = transport
        self.flag = flag


    async def post_inbox(self, request):
        json_val = await request.json()
        return PlainTextResponse(
                f"Hello {request.path_params['username']}! {json_val['msg']}")


    async def get_remote_flag(self, request):
        json_val = await request.json()
        dest = json_val['dest']
        which_flag = json_val['msg']
        url_to_call = f"https://{dest}/get_local_flag?flag={which_flag}"
        flag = await self.transport.get_json(url_to_call)
        return JSONResponse(json.loads(flag)) 


    async def get_local_flag(self, request):
        which_flag = request.query_params['flag']
        response = JSONResponse({ 'flag' : 'hello' })
        return response
        

    def get_routes(self):
        routes = [
                Route("/inbox/{username}", endpoint = self.post_inbox, methods=['POST']),
                Route("/get_remote_flag", endpoint = self.get_remote_flag, methods=['POST']),
                Route("/get_local_flag", endpoint = self.get_local_flag, methods=['GET']),
                ]
        return routes


@asynccontextmanager
async def async_lifespan_gw(app):

    app.running = True
    gateway = AsyncGateway()
    app.transport.set_gateway(gateway)
    await gateway.start(app)

    yield

    app.running = False
    await gateway.stop()

 
