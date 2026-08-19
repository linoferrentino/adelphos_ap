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
import base64
import hashlib
import re
import uuid


from app.federation.BaseSocialGateway import BaseSocialGateway
from starlette.responses import Response
from app.sdc.Dependencies import Dependencies
from starlette.exceptions import HTTPException
from urllib.parse import urlsplit
from app.logging import gCon
from app.dao.ApActorDto import create_remote_actor
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


class ActivityPubGateway(BaseSocialGateway):


    def __init__(self, kernel):
        super().__init__(kernel)


    def _filter_message_type(self, body_ob):
        req_type = body_ob.get('type')
        if req_type == 'Follow':
            raise HTTPException(202, "No op.")
        elif req_type == 'Delete':
            raise HTTPException(202, "No op.")
        elif req_type != 'Create':
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
            return (None, False)

        key_id_val = keyId.split("=")[1][1:-1]

        actor_dto = await self._actor_get_or_discover(key_id_val) 

        digest_body = base64.b64encode(hashlib.sha256(
            body_str.encode('utf-8')).digest())

        digest_body_total = "SHA-256=" + digest_body.decode('utf-8')
        digest_sign = headers['digest']

        if (digest_body_total != digest_sign):
            return (None, False)

        date_str = headers['date']
        date_val = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
        current_date = datetime.now(timezone.utc)
        current_date = current_date.replace(tzinfo = None)
        time_diff = current_date - date_val
        total_secs = abs(time_diff.total_seconds())

        if (total_secs > 30):
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

        remote_public_key = actor_dto.get_public_key_bytes()

        try:
            remote_public_key.verify(
                    base64.b64decode(signature_field),
                    signature_text_bin,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                    )

        except Exception as err:
            return (None, False)

        return (actor_dto, True)

    
    async def _parse_message(self, user, request, actor_str, body_str, body_ob):

        object_body = body_ob.get('object')
        if object_body is None:
            raise HTTPException(401, "Malformed json, no body")

        if (isinstance(object_body, str)):
            raise HTTPException(401, "Malformed json, no body")

        content = object_body.get('content')
        if (content is None):
            raise HTTPException(401, "No content in object {object_body}")

        clean_content = re.sub('<[^<]+?>', '', content) 

        return clean_content


    def _do_envelope(self, actor_from_dto, actor_to_dto, msg):

        #msg = re.sub("\n", "<p>", msg)
        paragraphs = [f"<p>{p.strip()}</p>" for p in re.split(r'\n+', msg) if p.strip()]
        html_msg = "".join(paragraphs) if paragraphs else "<p></p>"
        gCon.log(f"message has become {html_msg}")

        id_message = uuid.uuid4()

        sender_url = actor_from_dto.get_uri()
        actor_uri = actor_to_dto.get_uri()

        current_date = datetime.now(timezone.utc).strftime(
            '%a, %d %b %Y %H:%M:%S GMT')

        payload = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"{sender_url}/posts/{id_message}/activity",
            "type": "Create",
            "actor": sender_url,
            "to" : [
                actor_uri
            ],
            "cc" : [],
            "object": {
                "id": f"{sender_url}/posts/{id_message}",
                "type": "Note",
                "attributedTo": sender_url,
                "to": [actor_uri],
                "content": html_msg,
                "tag" : [
                    { 
                     "type" : "Mention",
                     "href" : actor_uri,
                     "name" : actor_to_dto.get_social_handle(),
                    },
                ],
                }
        }

        payload_str = json.dumps(payload, separators=(',',':'))

        digest = base64.b64encode(hashlib.sha256(
            payload_str.encode('utf-8')).digest())

        signature_text = b'(request-target): post %s\ndigest: SHA-256=%s\nhost: %s\ndate: %s' % (
             actor_to_dto.act.inbox_path.encode('utf-8'), digest,
             actor_to_dto.srv.host_name.encode('utf-8'),
             current_date.encode('utf-8'))

        sign_utf8 = signature_text.decode('utf-8')

        raw_signature = actor_from_dto.get_private_key_bytes().sign(
                signature_text,
                padding.PKCS1v15(),
                hashes.SHA256()
                )

        signature_str = base64.b64encode(raw_signature).decode('utf-8') 

        sender_key = actor_from_dto.get_key_uri()

        signature_header = f'keyId="{sender_key}",algorithm="rsa-sha256",headers="(request-target) digest host date",signature="{signature_str}"' 

        headers = {
            'date': current_date,
            'content-type': 'application/activity+json',
            'host': actor_to_dto.srv.host_name,
            'digest': "SHA-256="+digest.decode('utf-8'),
            'signature': signature_header
            }

        return (headers, payload_str) 


