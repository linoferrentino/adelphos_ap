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
from app.federation.BaseSocialGateway import BaseSocialGateway
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from app.sdc.Dependencies import Dependencies
from starlette.responses import Response
from app.logging import gCon
from starlette.exceptions import HTTPException
from urllib.parse import urlsplit


class SimpleSocialGateway(BaseSocialGateway):


    def __init__(self, vhost):
        super().__init__(vhost)


    def _filter_message_type(self, body_ob):
        pass


    async def _parse_message(self, user, request, actor_str, body_str, body_ob):
        gCon.log(f"Message from actor {actor_str} to {user}")
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        local_recipient = social.local_user_get(user)
        if local_recipient is None:
            raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST)
        msg = body_ob['msg']
        return (local_recipient, msg)


    async def _check_signature_message(self, actor_str, request, body_str):
        gCon.log(f"checking signature for {actor_str}")
        actor_split = urlsplit(actor_str)
        actor_dto = await self._actor_get_or_discover(actor_split)
        if actor_dto is None:
            gCon.log(f"No actor! {actor_split}")
            return (None, False)
        return (actor_dto, True)


    async def _actor_get_or_discover(self, uri):
        social_dao = self.vhost.get_dep(Dependencies.SOCIAL_DAO)
        actor_dto = social_dao.actor_get_from_parsed_url(uri)
        if actor_dto is not None:
            return actor_dto
        if len(uri.netloc) == 0:
            return None
        gCon.log(f"to do the netloc {uri.netloc}")


    async def in_inbox__OLD(self, user, request):

        headers = request.headers
        gCon.log(f"here are the headers {headers}")
        gCon.log(f"here is the url {request.url} type {type(request.url)}")
        gCon.log(f"here is the client {request.client} type {type(request.client)}")

        social = self.vhost.get_dep(Dependencies.SOCIAL)

        body = await request.body()
        gCon.log(f"the body is {body}")

        json = await request.json()
        await social.incoming_message(user, json)
        return Response(status_code=202)


