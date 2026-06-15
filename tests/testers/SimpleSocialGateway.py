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
        actor_dto = await self._actor_get_or_discover(actor_str)

        headers = request.headers
        
        signature = headers.get('x-simple-signature')
        if signature is None:
            gCon.log("NO signature")
            raise AdelphosException(AdErrno.EINVALID_SIGNATURE)

        gCon.log(f"checking signature for {actor_str}, signature {signature}")

        if actor_dto is None:
            gCon.log(f"No actor! {actor_str}")
            return (None, False)
        return (actor_dto, True)


    def _do_envelope(self, actor_from_dto, actor_to_dto, message):
        actor_uri = actor_from_dto.get_uri()
        headers = {
                'x-simple-signature' : f"{message[:3]}-{message[-3:]}"
                }
        return ( headers, { 
                'actor' : actor_uri,
                'msg' : message,
                })

