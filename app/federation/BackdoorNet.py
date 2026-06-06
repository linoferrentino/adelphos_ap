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


from app.sdc.Dependency import Dependency
from app.federation.BackdoorRouter import BackdoorRouter
from starlette.routing import Route
import app.consts as CNST
from app.logging import gCon
from starlette.responses import Response


class BackdoorNet(BackdoorRouter):
    

    def __init__(self, vhost):
        super().__init__(vhost)


    async def _backdoor_post(self, request):
        gCon.log(f"backdoor!")
        return Response(status_code=202)


    def get_backdoor_routes(self):
        routes = [
                Route(CNST.BACKDOOR_ROUTE,
                      endpoint = self._backdoor_post, methods=['POST']),
                 ]
        return routes

