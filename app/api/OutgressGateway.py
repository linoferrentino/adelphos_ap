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
import requests
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

ADELPHOS_ERROR_CODES = {



}



def post_response(ctx):

    #actor_inbox = actor_str + "/inbox"
    actor_inbox = ctx.key_ob['inbox']

    #gCon.log(f"will send to {actor_inbox}")

    host = ctx.app.config['General']['host']
    host_api = host + API_POINT

    sender_url = f"https://{host_api}/users/{USER_ID}"
    sender_key = f"{sender_url}#main-key"

    current_date = datetime.now().strftime(
            '%a, %d %b %Y %H:%M:%S GMT')

    recipient_parsed = urlparse(actor_inbox)
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
                "to": [ctx.actor_str],
                "content": f"{ctx.answer_txt}",
                }

            }

    new_message_str = json.dumps(new_message)

    digest = base64.b64encode(hashlib.sha256(
        new_message_str.encode('utf-8')).digest())

    signature_text = b'(request-target): post %s\ndigest: SHA-256=%s\nhost: %s\ndate: %s' % (recipient_path.encode('utf-8'), digest, recipient_host.encode('utf-8'), current_date.encode('utf-8'))

    sign_utf8 = signature_text.decode('utf-8')

    #gCon.log(f"This is my signature\n{sign_utf8}")

    raw_signature = ctx.app.private_key.sign(
            signature_text,
            padding.PKCS1v15(),
            hashes.SHA256()
            )

    #print(f"sender {sender_key}")
    signature_str = base64.b64encode(raw_signature).decode('utf-8') 
    #print(f"signature {signature_str}")

    signature_header = f'keyId="{sender_key}",algorithm="rsa-sha256",headers="(request-target) digest host date",signature="{signature_str}"' 

    #print(f"total {signature_header}")
    headers = {
            'Date': current_date,
            'Content-Type': 'application/activity+json',
            'Host': recipient_host,
            'Digest': "SHA-256="+digest.decode('utf-8'),
            'Signature': signature_header
            }


    r = requests.post(actor_inbox, headers=headers, 
                      json=new_message)

    #gCon.log(f"Sent message, output {r.status_code}")

