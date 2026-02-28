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
# This is the ingress gateway, the entry point for the Activity Pub posts to the daemon

from app.ap_api.AsyncRequest import AsyncPostReq
from app.consts import API_POINT
from app.consts import USER_ID
from app.logging import gCon
from app.api.Dispatcher import dispatch_request
import base64
import json
import re
import hashlib
import uuid
from datetime import datetime
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import asyncio
from app.dao.AliasDto import AliasDto
from app.ap_api.AsyncRequest import AsyncGetReq
from urllib.parse import urlparse
from app.api.AppCtx import AppCtx
import asyncio
from app.api.ApAliasApi import ApAliasApi


# checks the validity of the message received.
# DEPRECATED
async def check_message(ctx):

    request = ctx.request
    body_str = ctx.body_str
    body_ob = ctx.body_ob

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
    gCon.log(f"Try to get the cached actor's key {ctx.actor_str}")

    # get the actor and server objectx.
    # I have the key, which is an URI, I parse it in its components.
    key_parsed = urlparse(key_id_val)

    ctx.server_dto = ctx.app.dao.ap_server_dao.get_or_create_from_uri(key_parsed)
    gCon.log(f"This is my server {ctx.server_dto}")

    ctx.actor_dto = await ctx.app.dao.ap_actor_dao\
            .get_or_discover_from_uri(ctx.server_dto, key_parsed)

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
        gCon.log("Too much drift in time!")
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

    gCon.log(f"the signature is\n{signature_text}")

    signature_text_bin = signature_text.encode('utf-8')

    remote_public_key = crypto_serialization.load_pem_public_key(
            ctx.actor_dto.public_key.encode(),
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


# this is the object which will process the requests that come from
# Activity Pub
class ActivityPubGateway(AppCtx):


    def __init__(self, app):
        super().__init__(app)

        # this is the Activity Pub actor which has issued the request.
        # probably this does not need to be here.
        self.actor_str = None

        # the two objects which represent the verified sender of the message
        # (it can also be a bot: another adelphos daemon).
        self.actor_dto = None
        self.server_dto = None

        # I create here the daemon_api: it will register itself, and register
        # its handlers.
        self.ap_alias_api = ApAliasApi(self)


    # the ``ingress'' in activity pub is one-shot. The protocol is stateless.
    # this returns a code.
    #async def ingress(self, request):
    #    self.request = request
    #    return await _ingress_request(self)


    # this is the procedural request, it is asynchrously
    async def _proc_request_impl(self):

        # actually the activity pub gateway has only three important messages.
        # the alias create, the daemon_q and daemon_a, all the others are
        # handled by the web context.

        gCon.log("proc request in another thread.")
        await asyncio.sleep(3)
        gCon.log("After waiting I send the result")

        # maybe here I can wait the async context.
        return "ALL DONE"


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
        if ( mention != f"@{USER_ID}"):
            gCon.log(f"This is not a message for me. {mention}")
            return (400, None)

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


    # here the outgress result, in our case it will post the message to the
    # user's inbox who has made the request.
    async def outgress_result(self, result):
        gCon.log(f"outgress result {result}")

        host_name = self.server_dto.host_name
        user_path = self.actor_dto.user_path
        inbox_path = self.actor_dto.inbox_path

        actor_uri = f"https://{host_name}{user_path}"
        inbox_uri = f"https://{host_name}{inbox_path}"

        # Simple format, just convert the new lines
        #gCon.log(f"You want to send {msg}")
        msg = re.sub("\n", "<p>", result)
        #gCon.log(f"Now you have {msg}")

        host = self.app.get_local_host() 
        host_api = host + API_POINT

        sender_url = f"https://{host_api}/users/{USER_ID}"
        sender_key = f"{sender_url}#main-key"

        current_date = datetime.now().strftime(
                '%a, %d %b %Y %H:%M:%S GMT')

        id_message = uuid.uuid4()

        new_message = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{sender_url}/posts/{id_message}/activities",
                "type": "Create",
                "actor": sender_url,
                "object": {
                    "id": f"{sender_url}/posts/{id_message}",
                    "type": "Note",
                    "attributedTo": sender_url,
                    "to": [actor_uri],
                    "content": f"{result}",
                    }

                }

        new_message_str = json.dumps(new_message)

        digest = base64.b64encode(hashlib.sha256(
            new_message_str.encode('utf-8')).digest())

        signature_text = b'(request-target): post %s\ndigest: SHA-256=%s\nhost: %s\ndate: %s' % (inbox_path.encode('utf-8'), digest, host_name.encode('utf-8'), current_date.encode('utf-8'))

        sign_utf8 = signature_text.decode('utf-8')

        raw_signature = self.app.private_key.sign(
                signature_text,
                padding.PKCS1v15(),
                hashes.SHA256()
                )

        signature_str = base64.b64encode(raw_signature).decode('utf-8') 

        signature_header = f'keyId="{sender_key}",algorithm="rsa-sha256",headers="(request-target) digest host date",signature="{signature_str}"' 

        headers = {
                'Date': current_date,
                'Content-Type': 'application/activity+json',
                'Host': host_name,
                'Digest': "SHA-256="+digest.decode('utf-8'),
                'Signature': signature_header
                }

        #gCon.log(f"just before sending to {inbox_uri}")
        #gCon.log(f"{new_message}")
        post_res  = AsyncPostReq(inbox_uri, headers, new_message)
        await self.app.async_req_push(post_res)


# here ctx is ``self'' , an ActivityPubIngressGateway, (just a temporary hack)
# DEPRECATED
async def _ingress_request(ctx) -> int:

    ctx.body = await ctx.request.body()
    ctx.body_str = ctx.body.decode()

    ctx.body_ob = json.loads(ctx.body_str)
    ctx.actor_str = ctx.body_ob['actor']

    gCon.rule(f"Start processing from {ctx.actor_str}")
    gCon.log(f"For: url {ctx.request.url}")

    ctx.object_body = ctx.body_ob['object']

    if (isinstance(ctx.object_body, dict) == False):
        gCon.log(f"what is it? {str(ctx.object_body)}")
        return (400, None)

    #gCon.log(f"{ctx.object_body}")
    content = ctx.object_body.get('content')
    if (content is None):
        gCon.log(f"No content in object {ctx.object_body}")
        return (401, None)

    # remove HTML tags
    ctx.clean_content = re.sub('<[^<]+?>', '', content) 

    gCon.log(f"Message: [yellow]{ctx.clean_content}[/yellow]")

    ob_type = ctx.body_ob['type']

    # I only understand activity create post objects.
    if (ob_type != 'Create'):
        gCon.log(f"Unrecognized activity type {ob_type}")
        return (400, None)

    object_body_type = ctx.object_body['type']
    if (object_body_type != 'Note'):
        gCon.log(f"Unrecognized object internal type {object_body_type}")
        return (400, None)

    valid_ob = await check_message(ctx)

    if (valid_ob == False):
        return (401, None)
    
    #asyncio.create_task(dispatch_request(ctx)) 

    # the message has been accepted, I will return the response after.
    return (202, ctx.clean_content)

