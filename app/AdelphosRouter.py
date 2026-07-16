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
from app.endpoints.AdelphosDaemonCli import AdelphosDaemonCli
from app.endpoints.AdelphosWebSocket import AdelphosWebSocket
from app.federation.SocialProvider import SocialProvider
from app.federation.ap.ActivityPubNetwork import ActivityPubNetwork

from app.cli.AdelphosCliRouter import AdelphosCliRouter

import app.sdc.s_utils as sdc
from app.sdc.Dependencies import Dependencies


class AdelphosRouter(Routable):


    def __init__(self, kernel):
        super().__init__(kernel)
  
        
    #def get_dep(self, dep):
    #    return self.vhost.get_dep(dep)


    #def conf(self):
    #    return self.vhost.conf()


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


# I initialize the router with the app.
#class AdelphosRouter_deprecated(APIRouter):
class AdelphosRouter_deprecated():


    def __init__(self, app):
        super().__init__()
        self.app = app


def make_router(app):

    router = AdelphosRouter(app)

    test_instance = app.is_test_instance()

    if test_instance:
        # I can add a backdoor to test the application (in testing).
        @router.post('/_backdoor_api_/{cmd}')
        async def _backdoor_api(cmd: str, request : Request):
            body = await request.body()
            body_str = body.decode()
            body_ob = json.loads(body_str)
            ap_mock = app.get_ap_mockup()
            # the mock might as well do other async calls
            res = await ap_mock.proc_cmd(cmd, body_ob)
            #gCon.log(f"===================================== {res}")
            return { 'res' : res }


    @router.get("/daemon_cli")
    async def daemon_cli_inner():
        return await router.daemon_cli(app)
   

    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        client = await app.conn_hndl.accept(websocket)
        await client.serve_forever()



