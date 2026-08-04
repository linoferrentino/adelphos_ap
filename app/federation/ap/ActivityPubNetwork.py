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
import traceback

from starlette.routing import Route
from starlette.routing import WebSocketRoute
from starlette.responses import Response
from starlette.responses import JSONResponse
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket

import app.consts as CNST
from app.logging import gCon

from app.transport.Routable import Routable
from app.federation.SocialProvider import SocialProvider

from app.federation.SocialNetwork import SocialNetwork
from app.sdc.Dependencies import Dependencies


class ActivityPubNetwork(SocialNetwork):

    def __init__(self, kernel):
        super().__init__(kernel)


    async def in_webfinger(self, request):
        resource = request.query_params.get('resource')
        if resource is None:
            return Response(status_code = 401)

        ap_user_match = re.match('acct:(.*?)@(.*)$', resource)
        if (ap_user_match is None):
            return Response(status_code=401)

        ap_user_rex = ap_user_match.group(1)
        ap_host_rex = ap_user_match.group(2)

        config = self.conf
        host = config.get_host()

        if ap_host_rex != host:
            return Response(status_code=404)

        social = self.kernel.get_dep(Dependencies.SOCIAL)
        user = social.local_user_get(ap_user_rex)

        if user is None:
            return Response(status_code=404)

        root_path = config.get_root_path()

        host_api = f"{host}{root_path}"

        response = JSONResponse(
            content={
                "subject": resource,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/activity+json",
                        "href": f"https://{host_api}/users/{ap_user_rex}"
                    }
                ]
            }
        )
        
        response.headers['Content-Type'] = 'application/jrd+json'
        return response


    async def in_infouser(self, request):
        username = request.path_params['username']
        social = self.kernel.get_dep(Dependencies.SOCIAL)
        userob = social.local_user_get(username)
        config = self.conf
        host = config.get_host()
        if userob is None:
            gCon.log(f"{host}: not found user {username}")
            return Response(status_code=404)

        root_path = config.get_root_path()
        host_api = f"{host}{root_path}"

        info_user = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": f"https://{host_api}/users/{username}",
            "inbox": f"https://{host_api}/users/{username}/inbox",
            "outbox": f"https://{host_api}/users/{username}/outbox",
            "type": 'Service' if userob.is_daemon else 'Person',
            "name": 'Adelphos daemon' if userob.is_daemon else \
                    f"Adelphos demo user {username}",
            "preferredUsername": userob.actor_dto.act.preferred_username,
            "publicKey": {
                "id": f"https://{host_api}/users/{username}#main-key",
                "type": "Key",
                "owner": f"https://{host_api}/users/{username}",
                "publicKeyPem": userob.actor_dto.act.public_key
            }
        }

        assert userob.actor_dto.act.public_key is not None
        response = JSONResponse(content = info_user)
        response.headers['Content-Type'] = 'application/activity+json'
        return response
    

    async def in_inbox(self, request):
        social_gw = self.kernel.get_dep(Dependencies.SOCIAL_GATEWAY)
        user = request.path_params['username']
        config = self.conf
        host = config.get_host()
        try:
            response = await social_gw.in_inbox(user, request)
            return response
        except Exception as ex:
            body = await request.body()
            gCon.log(f"{host}: got exception while delivering {body}")
            traceback.print_exc()
            return Response(status_code = 500)


    def in_outbox(self, request):

        return Response(status_code=405)


    def get_social_routes(self):
        routes = [
                Route(CNST.WEBFINGER_ROUTE,
                      endpoint = self.in_webfinger, methods=['GET']),
                Route(CNST.USER_DISCOVER_ROUTE, 
                      endpoint = self.in_infouser, methods=['GET']),
                Route(CNST.USER_INBOX_ROUTE,
                      endpoint = self.in_inbox, methods=['POST']),
                Route(CNST.USER_OUTBOX_ROUTE,
                      endpoint = self.in_outbox, methods=['GET']),
                ]
        return routes
