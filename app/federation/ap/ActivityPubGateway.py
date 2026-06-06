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
from urllib.parse import urlsplit
from app.logging import gCon
import re


class ActivityPubGateway(BaseSocialGateway):


    def __init__(self, vhost):
        super().__init__(vhost)


    async def _check_signature_message(self, actor_str, request, body_str):
        
        headers = request.headers

        signature = headers['signature']

        (keyId, algorithm, signed_headers, signature_val) = signature.split(",")

        signed_headers_list = signed_headers.split("=")[1][1:-1].split(" ")
        signature_field_list = signature_val.split("=", 1)
        signature_field_raw = signature_field_list[1]
        signature_field = signature_field_raw[1:-1]

        algo_id_val = algorithm.split("=")[1][1:-1]
        if (algo_id_val != "rsa-sha256"):
            gCon.log(f"unsupported algo {algo_id_val}")
            return False

        key_id_val = keyId.split("=")[1][1:-1]
        gCon.log(f"fetching the actor {key_id_val}")

        actor_dto = await self._actor_get_or_discover(key_id_val) 

        return True


    async def _actor_get_or_discover(self, uri):
        key_parsed = urlsplit(uri)
        gCon.log(f"the key parsed is {key_parsed}")
        social_dao = self.vhost.get_dep(Dependencies.SOCIAL_DAO)
        actor_dto = social_dao.actor_get_from_parsed_url(key_parsed)
        if actor_dto is not None:
            return actor_dto

        actor_uri_p = key_parsed._replace(fragment = "")
        actor_uri = actor_uri_p.geturl()
        gCon.log(f"actor_uri {actor_uri}")

        transport = self.vhost.get_dep(Dependencies.TRANSPORT)
        actor_ob = await transport.get_json(actor_uri)
        gCon.log(f"actor is {actor_ob}, type {type(actor_ob)}")

        server_dto = social_dao.srv_get_or_create(key_parsed.netloc)
        gCon.log(f"Server is {server_dto}")

    
    async def _parse_message(self, user, request, actor_str, body_str, body_ob):
        gCon.log(f"Message from actor {actor_str}")
        gCon.log(f"Message is {body_str}")

        req_type = body_ob.get('type')
        if req_type == 'Follow':
            gCon.log("Following request.")
            raise HTTPException(202, "No op.")
        elif req_type == 'Delete':
            gCon.log("Delete request.")
            raise HTTPException(202, "No op.")
        elif req_type != 'Create':
            gCon.log(f"unkown activity {req_type}")
            raise HTTPException(405, "No op.")

        object_body = body_ob.get('object')
        if object_body is None:
            raise HTTPException(401, "Malformed json, no body")

        if (isinstance(object_body, str)):
            gCon.log(f"Received str {object_body}")
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

        social = self.vhost.get_dep(Dependencies.SOCIAL)
        local_user= social.local_user_get(mention)

        if local_user is None:
            msg = f"User not found {mention}"
            gCon.log(msg)
            raise HTTPException(404, msg)

        return (None, local_user, clean_content)


