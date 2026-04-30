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

class TRoutable(Routable):


    async def post_inbox(self, request):
        json_val = await request.json()
        return PlainTextResponse(
                f"Hello {request.path_params['username']}! {json_val['msg']}")


    def get_routes(self):
        routes = [
                Route("/inbox/{username}", endpoint = self.post_inbox, methods=['POST'])
                ]
        return routes


