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


from app.federation.SocialGateway import SocialGateway
from app.exc.AdelphosException import AdelphosException
from app.sdc.Dependencies import Dependencies
from starlette.responses import Response
from app.logging import gCon


class SimpleSocialGateway(SocialGateway):


    def __init__(self, vhost):
        super().__init__(vhost)


    async def in_inbox(self, user, request):

        headers = request.headers
        gCon.log(f"here are the headers {headers}")
        gCon.log(f"here is the url {request.url} type {type(request.url)}")
        gCon.log(f"here is the client {request.client} type {type(request.client)}")

        social = self.vhost.get_dep(Dependencies.SOCIAL)
        body = await request.json()
        await social.incoming_message(user, body)
        return Response(status_code=202)


