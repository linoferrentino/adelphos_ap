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
from app.dao.ApActorDto import create_remote_actor
import json
import base64
import hashlib
import re
from datetime import datetime
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


class ActivityPubGateway(BaseSocialGateway):


    def __init__(self, vhost):
        super().__init__(vhost)


    def _filter_message_type(self, body_ob):
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
            return (None, False)

        key_id_val = keyId.split("=")[1][1:-1]
        gCon.log(f"fetching the actor {key_id_val}")

        actor_dto = await self._actor_get_or_discover(key_id_val) 

        digest_body = base64.b64encode(hashlib.sha256(
            body_str.encode('utf-8')).digest())

        digest_body_total = "SHA-256=" + digest_body.decode('utf-8')
        digest_sign = headers['digest']

        if (digest_body_total != digest_sign):
            gCon.log("digest mismatch, go away")
            return (None, False)

        date_str = headers['date']
        date_val = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
        current_date = datetime.now()
        time_diff = current_date - date_val
        total_secs = abs(time_diff.total_seconds())

        if (total_secs > 30):
            gCon.log(f"Too much drift in time! {total_secs}")
            return (None, False)

        host_hdr = headers['host']
        try:
            x_forwarded_prefix = headers['x-forwarded-prefix']
        except:
            x_forwarded_prefix = ""

        signature_text = ""
        for signed_header in signed_headers_list:
            signature_text += f"{signed_header}: "
            match signed_header:
                case '(request-target)':
                    signature_text += f"{str(request.method).lower()} \
{x_forwarded_prefix}{request.url.path}\n"
                case 'host':
                    signature_text += f"{host_hdr}\n"
                case 'date':
                    signature_text += f"{date_str}\n"
                case 'digest':
                    signature_text += f"{digest_body_total}\n"
                case "content-type":
                    signature_text += f"{headers['content-type']}\n"
                case _:
                    signature_text += f"INVALID {signed_header}\n"
        signature_text = signature_text[:-1]

        signature_text_bin = signature_text.encode('utf-8')

        remote_public_key = crypto_serialization.load_pem_public_key(
                actor_dto.public_key.encode(),
                backend=crypto_default_backend()
        )

        try:
            remote_public_key.verify(
                    base64.b64decode(signature_field),
                    signature_text_bin,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                    )
            gCon.log("[green]The signature is valid.[/green]")

        except Exception as err:
            gCon.log(f"[red]The signature is invalid.[/red]\n{err}")
            return (None, False)

        return (actor_dto, True)


    #async def _actor_get_or_discover(self, uri):
    #    key_parsed = urlsplit(uri)
    #    #gCon.log(f"the key parsed is {key_parsed}")
    #    social_dao = self.vhost.get_dep(Dependencies.SOCIAL_DAO)
    #    actor_dto = social_dao.actor_get_from_parsed_url(key_parsed)
    #    if actor_dto is not None:
    #        return actor_dto


    #async def _actor_discover_from_key(self, key_parsed):

    #    actor_uri_p = key_parsed._replace(fragment = "")
    #    actor_uri = actor_uri_p.geturl()
    #    #gCon.log(f"actor_uri {actor_uri}")

    #    transport = self.vhost.get_dep(Dependencies.TRANSPORT)
    #    actor_ob = await transport.get_json(actor_uri)
    #    #gCon.log(f"actor is {actor_ob}, type {type(actor_ob)}")

    #    key_ob = json.loads(actor_ob)

    #    gCon.log(f"The object requested is {key_ob}")

    #    pub_key_ob = key_ob['publicKey']
    #    pub_key_ob_id = pub_key_ob['id']

    #    if (pub_key_ob_id != key_parsed.geturl()):
    #        raise Exception(f"Error, got {pub_key_ob_id} key \
            #exp #{actor_uri}")

    #    owner = pub_key_ob['owner'] 
    #    if (owner != actor_uri):
    #        raise Exception(f"Bad key {owner} different from {actor_uri}")

    #    inbox_uri = key_ob['inbox']
    #    preferred_username = key_ob['preferredUsername']
    #    inbox_parsed = urlsplit(inbox_uri)

    #    server_dto = social_dao.srv_get_or_create(key_parsed.netloc)

    #    actor_dto = create_remote_actor(server_dto.server_id,
    #                     key_parsed.path,
    #                     inbox_parsed.path,
    #                     preferred_username,
    #                     pub_key_ob['publicKeyPem'])
    #    social_dao.actor_store(actor_dto)
    #    gCon.log(f"New actor {actor_dto}")
    #    return actor_dto

    
    async def _parse_message(self, user, request, actor_str, body_str, body_ob):
        gCon.log(f"Message from actor {actor_str}")
        gCon.log(f"Message is {body_str}")

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

        return (local_user, clean_content)


    def _do_envelope(self, actor_from_dto, message):
        pass


    #async def _actor_get_or_discover_from_handle(self, preferred_name):
    #    pass
