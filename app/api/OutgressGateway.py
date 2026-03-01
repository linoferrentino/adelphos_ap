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
import re


async def post_response(ctx):

    msg = ctx.answer_txt

    return await post_response_inbox(ctx, ctx.actor_dto, ctx.server_dto, msg)


async def post_daemon_req(ctx):

    msg = ctx.query_txt 

    return await post_response_inbox(ctx, ctx.daemon_dto,
                                     ctx.daemon_server_dto, msg)


async def post_response_inbox(ctx, actor, server, msg):
    return await post_response_inbox_impl(ctx, ctx.server_dto.host_name,
                                          ctx.actor_dto.user_path,
                                          ctx.actor_dto.inbox_path, msg)


async def post_to_ap_actor(app, server_dto, actor_dto, message):
    return await post_response_inbox_impl(app, server_dto.host_name, 
                                          actor_dto.user_path,
                                          actor_dto.inbox_path, message)


# we can pass messages to other inboxes, for example a daemon inbox 
async def post_response_inbox_impl(app, host_name, user_path, inbox_path, msg):


    actor_uri = f"https://{host_name}{user_path}"
    inbox_uri = f"https://{host_name}{inbox_path}"

    # Simple format, just convert the new lines
    #gCon.log(f"You want to send {msg}")
    msg = re.sub("\n", "<p>", msg)
    #gCon.log(f"Now you have {msg}")

    host = app.get_local_host()
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
                "content": f"{msg}",
                }

            }

    new_message_str = json.dumps(new_message)

    digest = base64.b64encode(hashlib.sha256(
        new_message_str.encode('utf-8')).digest())

    signature_text = b'(request-target): post %s\ndigest: SHA-256=%s\nhost: %s\ndate: %s' % (inbox_path.encode('utf-8'), digest, host_name.encode('utf-8'), current_date.encode('utf-8'))

    sign_utf8 = signature_text.decode('utf-8')

    raw_signature = app.private_key.sign(
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

    gCon.log(f"just before sending to {inbox_uri}")
    gCon.log(f"{new_message}")
    post_res  = AsyncPostReq(inbox_uri, headers, new_message)
    await app.async_req_push(post_res)



