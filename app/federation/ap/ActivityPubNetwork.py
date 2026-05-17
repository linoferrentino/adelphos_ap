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

import app.consts as CNST
from app.logging import gCon

from app.transport.Routable import Routable
from app.endpoints.AdelphosDaemonCli import AdelphosDaemonCli
from app.endpoints.AdelphosWebSocket import AdelphosWebSocket
from app.federation.SocialProvider import SocialProvider

from app.federation.SocialNetwork import SocialNetwork


class ActivityPubNetwork(SocialNetwork):

    def __init__(self, router):
        super().__init__(router)


    async def post_to_user(self, user, message):
        pass


    async def discover_user(self, user):
        pass


    async def in_webfinger(self, request):
        resource = request.query_params.get('resource')
        if resource is None:
            return Response(status_code = 401)

        ap_user_match = re.match('acct:(.*?)@(.*)$', resource)
        if (ap_user_match is None):
            return Response(status_code=401)

        ap_user_rex = ap_user_match.group(1)
        ap_host_rex = ap_user_match.group(2)
        host = self.router.get_host()

        if ap_host_rex != host:
            return Response(status_code=404)

        if (self.router.social.local_user_exists(ap_user_rex) == False):
            return Response(status_code=404)

        host_api = f"{host}/{CNST.API_POINT}"

        response = Response(
            content=json.dumps({
                "subject": resource,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/activity+json",
                        "href": f"https://{host_api}/users/{ap_user_rex}"
                    }
                ]
            })
        )
        
        response.headers['Content-Type'] = 'application/jrd+json'
        return response


    async def in_infouser(self, request):
        pass


    async def in_inbox(self, request):

        user = request.path_params['username']
        body = await request.json()
        await self.router.social.incoming_message(user, body)
        return Response(status_code=202)


    def get_social_routes(self):
        routes = [
                Route(CNST.WEBFINGER_ROUTE,
                      endpoint = self.in_webfinger, methods=['GET']),
                Route(CNST.USER_DISCOVER_ROUTE, 
                      endpoint = self.in_infouser, methods=['GET']),
                Route(CNST.USER_INBOX_ROUTE,
                      endpoint = self.in_inbox, methods=['POST']),
                ]
        return routes
