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
#
# This is the Activity Pub gateway, the entry point to Adelphos.


from app.ap_api.AsyncRequest import AsyncGetReq
from app.ap_api.AsyncRequest import AsyncPostReq
from app.api.ApAliasApi import ApAliasApi
from app.api.Gateway import Gateway
from app.consts import API_POINT
from app.consts import USER_ID
from app.consts import DAEMON_ID
from app.dao.AliasDto import AliasDto
from app.logging import gCon
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime
from urllib.parse import urlparse
from app.api.OutgressGateway import post_to_ap_actor
import asyncio
import asyncio
import base64
import hashlib
import json
import re
import uuid
from abc import abstractmethod


# this is the object which will process the requests that come from
# Activity Pub
class ActivityPubBaseGateway(Gateway):


    def __init__(self, app):
        super().__init__(app)

        # the two objects which represent the verified sender of the message
        # (it can also be a bot: another adelphos daemon).
        self.actor_dto = None
        self.server_dto = None


    # check an ActivityPub message using the W3C reccomendations
    async def check_ap_message(self, actor_str, request, body_str): 

        headers = request.headers

        signature = headers['signature']

        # this is the serialized object, we take the fields
        (keyId, algorithm, signed_headers, signature_val) = signature.split(",")

        # transform the string into a list.
        signed_headers_list = signed_headers.split("=")[1][1:-1].split(" ")
        signature_field_list = signature_val.split("=", 1)
        signature_field_raw = signature_field_list[1]
        signature_field = signature_field_raw[1:-1]

        algo_id_val = algorithm.split("=")[1][1:-1]
        if (algo_id_val != "rsa-sha256"):
            gCon.log(f"unsupported algo {algo_id_val}")
            return False

        # Now we try to get the public key 
        key_id_val = keyId.split("=")[1][1:-1] #remove the quotes

        gCon.log(f"Get the public key {key_id_val}")
        gCon.log(f"Try to get the cached actor's key {actor_str}")

        # get the actor and server objectx.
        # I have the key, which is an URI, I parse it in its components.
        key_parsed = urlparse(key_id_val)

        self.server_dto = self.app.dao.ap_server_dao.get_or_create_from_uri(key_parsed)
        gCon.log(f"This is my server {self.server_dto}")

        self.actor_dto = await self.app.dao.ap_actor_dao\
                .get_or_discover_from_uri(self.server_dto, key_parsed)

        ####### 1st, Check the digest
        digest_body = base64.b64encode(hashlib.sha256(
            body_str.encode('utf-8')).digest())

        digest_body_total = "SHA-256=" + digest_body.decode('utf-8')
        digest_sign = headers['digest']

        if (digest_body_total != digest_sign):
            gCon.log("digest mismatch, go away")
            return False

        ####### 2nd check date
        date_str = headers['date']

        date_val = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')

        current_date = datetime.now()

        time_diff = current_date - date_val

        total_secs = abs(time_diff.total_seconds())

        if (total_secs > 30):
            gCon.log(f"Too much drift in time! {total_secs}")
            return False

        # first of all we build the signature string to validate
        host_hdr = headers['host']

        # to verify the signature, I have to add the prefix
        try:
            x_forwarded_prefix = headers['x-forwarded-prefix']
        except:
            x_forwarded_prefix = ""

        # at first it is empty
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
            
        # I remove the last newline
        signature_text = signature_text[:-1]

        #gCon.log(f"You want to verify\n{signature_text}")

        signature_text_bin = signature_text.encode('utf-8')

        remote_public_key = crypto_serialization.load_pem_public_key(
                self.actor_dto.public_key.encode(),
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
            return False

        return True



    # this function will check the validity of the request and return a string
    async def pre_process_request(self, request):
        gCon.log("pre proc request")

        body = await request.body()
        body_str = body.decode()

        body_ob = json.loads(body_str)
        actor_str = body_ob['actor']

        object_body = body_ob['object']

        if (isinstance(object_body, dict) == False):
            gCon.log(f"Cannot understand: {str(object_body)}")
            return (400, None)

        content = object_body.get('content')
        if (content is None):
            gCon.log(f"No content in object {object_body}")
            return (401, None)

        # remove HTML tags
        clean_content = re.sub('<[^<]+?>', '', content) 

        gCon.rule(f"Message from {actor_str}")
        gCon.log(f"For: url {request.url}")
        gCon.log(f"Message: [yellow]{clean_content}[/yellow]")

        # the message must be for the ActivityPub daemon
        (mention, rest_of_line) = clean_content.split(" ", 1)
        if mention[0] != '@':
            gCon.log(f"Malformed mention {mention}")
            return (400, None)
        mention = mention[1:]
        if self.ap_user_exists(mention) == False:
            gCon.log(f"User not found in this instance {mention}")
            return (404, None)

        #if ( mention != f"@{self.user}"):
        #    gCon.log(f"This is not a message for me. Got: {mention}")
        #    return (400, None)

        ob_type = body_ob['type']

        # I only understand activity create post objects.
        if (ob_type != 'Create'):
            gCon.log(f"Unrecognized activity type {ob_type}")
            return (400, None)

        object_body_type = object_body['type']
        if (object_body_type != 'Note'):
            gCon.log(f"Unrecognized object internal type {object_body_type}")
            return (400, None)

        valid_ob = await self.check_ap_message(actor_str, request, body_str)

        # no valid message, no party
        if (valid_ob == False):
            return (401, None)
        
        # the message has been accepted, I will return the response after.
        return (202, rest_of_line)


    # this method is redefined in the MockupGateway which will accept posted
    # messages for the users.
    @abstractmethod
    def ap_user_exists(self, activity_pub_user):
        return False


    # here the outgress result, in our case it will post the message to the
    # user's inbox who has made the request.
    async def outgress_result(self, result):

        #await post_to_ap_actor(self.app, self.server_dto,
        #                       self.actor_dto, result)
        await self.app.ap_api.post_to_fediverse_actor_as_daemon(
                self.server_dto, self.actor_dto, result)


class ActivityPubGateway(ActivityPubBaseGateway):

    
    def __init__(self, app):
        super().__init__(app)
        # I create here the daemon_api: it will register itself, and register
        # its handlers.
        self.ap_alias_api = ApAliasApi(self)


    def ap_user_exists(self, activity_pub_user):
        if activity_pub_user == DAEMON_ID:
            return True
        return False


