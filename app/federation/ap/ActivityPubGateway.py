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


from app.federation.BaseSocialGateway import BaseSocialGateway
from starlette.responses import Response
from app.sdc.Dependencies import Dependencies
from starlette.exceptions import HTTPException
from app.logging import gCon
import re


class ActivityPubGateway(BaseSocialGateway):


    def __init__(self, vhost):
        super().__init__(vhost)


    async def _parse_message(self, user, request, actor_str, body_str, body_ob):
        gCon.log(f"Message from actor {actor_str}")

        object_body = body_ob.get('object')
        if object_body is None:
            raise HTTPException(401, "Malformed json, no body")

        content = object_body.get('content')
        if (content is None):
            raise HTTPException(401, "No content in object {object_body}")

        clean_content = re.sub('<[^<]+?>', '', content) 
        gCon.log(f"message is {clean_content}")

        (mention, rest_of_line) = clean_content.split(" ", 1)
        if mention[0] != '@':
            raise HTTPException(400, f"Malformed mention {mention}")

        mention = mention[1:]

        local_actor = social_dao.actor_get_local(mention)

        if local_actor is None:
            raise HTTPException(404, f"User not found {mention}")



        return (None, None, clean_content)


