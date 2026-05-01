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



class TRoutable(Routable):


    def __init__(self, transport, flag):
        self.transport = transport


    async def post_inbox(self, request):
        json_val = await request.json()
        return PlainTextResponse(
                f"Hello {request.path_params['username']}! {json_val['msg']}")


    async def post_msg_q(self, request):
        self.transport.get_json(


    async def post_msg_a(self, request):
        json_val = await request.json()
        global flag
        flag = json_val['msg']
        return Response(202, None)


    def get_routes(self):
        routes = [
                Route("/inbox/{username}", endpoint = self.post_inbox, methods=['POST']),
                Route("/get_flag", endpoint = self.post_msg_q, methods=['GET']),
                Route("/post_flag", endpoint = self.post_msg_a, methods=['POST'])
                ]
        return routes


