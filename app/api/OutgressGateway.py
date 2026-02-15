# this is the gateway that posts the answer.

# remember that the answer is not given synchronously,


from app.consts import API_POINT
from app.consts import USER_ID
from app.logging import gCon
import uuid
import json
import base64
import hashlib
from urllib.parse import urlparse
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from app.ap_api.AsyncRequest import AsyncPostReq


#ADELPHOS_ERROR_CODES = {
#
#}
#


async def post_response(ctx):

    msg = ctx.answer_txt

    return await post_response_inbox(ctx, ctx.actor_dto, ctx.server_dto, msg)


#async def post_to_actor_inbox(ctx, msg):
#
#    return await post_response_inbox(ctx, ctx.actor.actor_uri,
#                                     ctx.actor.inbox_uri, msg)


async def post_daemon_req(ctx):

    msg = ctx.query_txt 

    return await post_response_inbox(ctx, ctx.daemon_dto,
                                     ctx.daemon_server_dto, msg)


async def post_response_inbox(ctx, actor, server, msg):
    actor_uri = f"https://{ctx.server_dto.host_name}/\
{ctx.actor_dto.user_path}"
    inbox_uri = f"https://{ctx.server_dto.host_name}\
{ctx.actor_dto.inbox_path}"
    return await post_response_inbox_impl(ctx, actor_uri, inbox_uri, msg)



# we can pass messages to other inboxes, for example a daemon inbox 
async def post_response_inbox_impl(ctx, actor_str, inbox, msg):


    host = ctx.app.config['General']['host']
    host_api = host + API_POINT

    sender_url = f"https://{host_api}/users/{USER_ID}"
    sender_key = f"{sender_url}#main-key"

    current_date = datetime.now().strftime(
            '%a, %d %b %Y %H:%M:%S GMT')

    recipient_parsed = urlparse(inbox)
    recipient_host = recipient_parsed.netloc
    recipient_path = recipient_parsed.path

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
                "to": [actor_str],
                "content": f"{msg}",
                }

            }

    new_message_str = json.dumps(new_message)

    digest = base64.b64encode(hashlib.sha256(
        new_message_str.encode('utf-8')).digest())

    signature_text = b'(request-target): post %s\ndigest: SHA-256=%s\nhost: %s\ndate: %s' % (recipient_path.encode('utf-8'), digest, recipient_host.encode('utf-8'), current_date.encode('utf-8'))

    sign_utf8 = signature_text.decode('utf-8')

    raw_signature = ctx.app.private_key.sign(
            signature_text,
            padding.PKCS1v15(),
            hashes.SHA256()
            )

    signature_str = base64.b64encode(raw_signature).decode('utf-8') 

    signature_header = f'keyId="{sender_key}",algorithm="rsa-sha256",headers="(request-target) digest host date",signature="{signature_str}"' 

    headers = {
            'Date': current_date,
            'Content-Type': 'application/activity+json',
            'Host': recipient_host,
            'Digest': "SHA-256="+digest.decode('utf-8'),
            'Signature': signature_header
            }


    gCon.log(f"just before sending to {inbox}")
    post_res  = AsyncPostReq(inbox, headers, new_message)
    await ctx.app.async_req_push(post_res)



