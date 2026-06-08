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
from abc import abstractmethod, ABC
from app.logging import gCon
from starlette.responses import Response
from starlette.exceptions import HTTPException
from app.sdc.Dependencies import Dependencies


class BaseSocialGateway(SocialGateway):

    def __init__(self, vhost):
        super().__init__(vhost)


    async def in_inbox(self, user, request):

        headers = request.headers
        gCon.log(f"here are the headers {headers}")
        gCon.log(f"here is the url {request.url} type {type(request.url)}")
        gCon.log(f"here is the client {request.client} type {type(request.client)}")

        body = await request.body()
        gCon.log(f"body {body}")
        body_str = body.decode()
        body_ob = await request.json()

        self._filter_message_type(body_ob)

        actor_str = body_ob.get('actor')
        if actor_str is None:
            raise HTTPException(401, "Malformed request, no actor")

        if await self._check_signature_message(actor_str, request, body_str) == False:
            raise HTTPException(401, "Invalid signature")
        
        (actor_from, local_recipient, content) = await self._parse_message(user,
                          request, actor_str, body_str, body_ob)

        social = self.vhost.get_dep(Dependencies.SOCIAL)
        await social.incoming_message(actor_from, local_recipient,  content)
        return Response(status_code=202)


    @abstractmethod
    def _filter_message_type(self, body_ob):
        pass


    @abstractmethod
    async def _parse_message(self, user, request, actor_str, body_str, body_ob):
        pass


    @abstractmethod
    async def _check_signature_message(self, actor_str, request, body_str):
        pass


    @abstractmethod
    async def _actor_get_or_discover(self, uri):
        pass
