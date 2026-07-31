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

import re
import json

from starlette.routing import Route
from starlette.routing import WebSocketRoute
from starlette.responses import Response
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket

from app.logging import gCon

from app.transport.Routable import Routable
from app.federation.SocialProvider import SocialProvider
from app.federation.ap.ActivityPubNetwork import ActivityPubNetwork

from app.cli.AdelphosCliRouter import AdelphosCliRouter

import app.sdc.s_utils as sdc
from app.sdc.Dependencies import Dependencies


class AdelphosRouter(Routable):


    def __init__(self, kernel):
        super().__init__(kernel)
  

    def set_transport(self, transport):
        self.kernel.set_dep(Dependencies.TRANSPORT, transport)


    def get_routes(self):
        routes = []
        social_net = self.get_dep(Dependencies.SOCIAL_NET)
        if social_net is not None:
            routes.extend(social_net.get_social_routes())
        cli_net = self.get_dep(Dependencies.CLI_NET)
        if cli_net is not None:
            routes.extend(cli_net.get_cli_routes())
        backdoor_net = self.get_dep(Dependencies.BACKDOOR_NET)
        if backdoor_net is not None:
            routes.extend(backdoor_net.get_backdoor_routes())
        return routes


    async def init_up(self):
        self.kernel.start_sync()
        await self.kernel.start_async()


    async def tear_down(self):
        await self.kernel.stop_async()
        self.kernel.stop_sync()



