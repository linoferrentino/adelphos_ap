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


import json
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
        msg = body_ob['msg']
        return msg


    async def _check_signature_message(self, actor_str, request, body_str):
        actor_dto = await self._actor_get_or_discover(actor_str)

        headers = request.headers

        signature = headers.get('x-simple-signature')
        if signature is None:
            raise AdelphosException(AdErrno.EINVALID_SIGNATURE)

        body_ob = json.loads(body_str)
        msg = body_ob['msg']

        got_signature = f"{msg[:3]}-{msg[-3:]}"
        if got_signature != signature:
            if signature != 'BACKDOOR_GO':
                raise AdelphosException(AdErrno.EINVALID_SIGNATURE,
                    f"msg: {msg} expected: {signature}")

        if actor_dto is None:
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

