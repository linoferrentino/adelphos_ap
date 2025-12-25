import typer
from urllib.parse import urlparse
import sys
import base64
from datetime import timedelta
from datetime import datetime

import json
import requests
import hashlib
import os
import uuid
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


from typing import Union
import asyncio
import requests

from fastapi import FastAPI
import json
from fastapi import APIRouter, Request, Depends, Query, HTTPException, status, Response

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.keys import load_keys, public_key, private_key
from app.logging import gCon
from app.config import load_conf
from app.config import get_config
from app.dao.AdelphosDao import AdelphosDao
import uvicorn
import re


ADELPHOS_AP_ENV_KEY = "ADELPHOS_AP_INSTANCE"


app = FastAPI(root_path="/api")


API_POINT = "/api"
HOST = "to_be_customized"
HOST_API = HOST + API_POINT

# this is equal for all the instances.
USER_ID = "daemon"

activity_id = "https://www.adelphos.it/users/bank/follows/test"


@app.get("/.well-known/webfinger",
    description="Adelphos's end point",
)
def webfinger(resource: str = Query(..., alias="resource")):

    #global HOST
    HOST = get_config()['General']['host']
    HOST_API = HOST + API_POINT

    print(f"------- host {HOST} resource {resource}")

    if resource != f"acct:{USER_ID}@{HOST}":
        return Response(status_code=404)

    response = Response(
        content=json.dumps({
            "subject": f"acct:{USER_ID}@{HOST}",
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"https://{HOST_API}/users/{USER_ID}"
                }
            ]
        })
    )
    
    response.headers['Content-Type'] = 'application/jrd+json'
    
    return response


@app.get('/users/{username}')
def user(username : str):
    HOST = get_config()['General']['host']
    HOST_API = HOST + API_POINT

    #global HOST_API
    #global USER_ID

    if username != USER_ID:
        return Response(status_code=404)

    response_ob = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
        ],
        "id": f"https://{HOST_API}/users/{USER_ID}",
        "inbox": f"https://{HOST_API}/users/{USER_ID}/inbox",
        "outbox": f"https://www.adelphos.it/users/{USER_ID}/outbox",
        "type": "Person",
        "name": "Adelphos' activity pub daemon",
        "preferredUsername": "daemon",
        "publicKey": {
            "id": f"https://{HOST_API}/users/{USER_ID}#main-key",
            "id": f"https://{HOST_API}/users/{USER_ID}",
            "publicKeyPem": public_key
        }
    }

    resp_json = jsonable_encoder(response_ob)

    response = JSONResponse(content = resp_json)

    response.headers['Content-Type'] = 'application/activity+json'

    return response



async def send_echo(actor_str: str):
    """Waits for a delay and then sends a reminder."""

    print("I wait 3 seconds")
    await asyncio.sleep(3)
    print(f"NOW I send it! to {actor_str}")
    # for now this is an assumption.
    actor_inbox = actor_str + "/inbox"
    print(f"I assume the inbox is: {actor_inbox}")

    HOST = get_config()['General']['host']
    HOST_API = HOST + API_POINT


    sender_url = f"https://{HOST_API}/users/{USER_ID}"
    sender_key = f"{sender_url}#main-key"



    current_date = datetime.now().strftime(
            '%a, %d %b %Y %H:%M:%S GMT')

    recipient_parsed = urlparse(actor_inbox)
    recipient_host = recipient_parsed.netloc
    recipient_path = recipient_parsed.path

    follow_request_message = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": activity_id,
            "type": "Create",
            "actor": sender_url,
            "object": {
                "id": f"{sender_url}/posts/{uuid.uuid4()}",
                "type": "Note",
                "attributedTo": sender_url,
                "to": [actor_str],
                "content": f"echo from daemon {current_date}",
                }

            }

    follow_request_json = json.dumps(follow_request_message)
    digest = base64.b64encode(hashlib.sha256(
        follow_request_json.encode('utf-8')).digest())

    signature_text = b'(request-target): post %s\ndigest: SHA-256=%s\nhost: %s\ndate: %s' % (recipient_path.encode('utf-8'), digest, recipient_host.encode('utf-8'), current_date.encode('utf-8'))

    sign_utf8 = signature_text.decode('utf-8')

    gCon.log(f"This is my signature\n{sign_utf8}")

    raw_signature = private_key.sign(
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
                      json=follow_request_message)

    gCon.log(f"Sent message, output {r.status_code}")


######
# code to verify the signature and the digest.

def check_message(request, body_str, body_ob):

    headers = request.headers

    signature = headers['signature']

    gCon.log(f"signature {signature} {type(signature)}")

    # this is the global object, now we take the fields

    (keyId, algorithm, signed_headers, signature_val) = signature.split(",")

    gCon.log(f"key id {keyId}")
    gCon.log(f"algorithm {algorithm}")
    gCon.log(f"signed headers {signed_headers}")
    gCon.log(f"signature_val {signature_val}")

    # transform the string into a list.
    signed_headers_list = signed_headers.split("=")[1][1:-1].split(" ")
    gCon.log(f"this is the list {signed_headers_list}")

    signature_field_list = signature_val.split("=", 1)

    gCon.log(f"Signature list {signature_field_list}")

    signature_field_raw = signature_field_list[1]

    gCon.log(f"sign field raw {signature_field_raw}")

    signature_field = signature_field_raw[1:-1]

    gCon.log(f"signature field is {signature_field}")


    # for now we support only sha-256 algo
    algo_id_val = algorithm.split("=")[1][1:-1]
    if (algo_id_val != "rsa-sha256"):
        gCon.log(f"unsupported algo {algo_id_val}")
        return False

    # Now we try to get the public key 
    key_id_val = keyId.split("=")[1][1:-1] #remove the quotes
    gCon.log(f"Get the public key {key_id_val}")

    headers_acc = {"Accept" : "application/activity+json"}

    res_key = requests.get(key_id_val, headers = headers_acc)

    gCon.log(f"this is the response {res_key}")

    if (res_key.status_code != 200):
        gCon.log()
        return False

    #gCon.log(res_key.headers)

    key_ob_text = res_key.text

    key_ob = json.loads(key_ob_text)

    pub_key_ob = key_ob['publicKey']

    pub_key_ob_id = pub_key_ob['id']
    pub_key_ob_pem = pub_key_ob['publicKeyPem']

    gCon.log(f"obtained id {pub_key_ob_id}")

    # are they the same?
    if (pub_key_ob_id != key_id_val):
        gCon.log("Error, got another key")
        return False

    gCon.log(f"this is the pem {pub_key_ob_pem}")


    ####### 1st, Check the digest
    digest_body = base64.b64encode(hashlib.sha256(
        body_str.encode('utf-8')).digest())

    digest_body_total = "SHA-256=" + digest_body.decode('utf-8')

    gCon.log(f"I expect {digest_body_total} as digest in headers")

    digest_sign = headers['digest']

    gCon.log(f"I got {digest_sign} as digest in headers")

    if (digest_body_total != digest_sign):
        gCon.log("digest mismatch, go away")
        return False

    ####### 2nd check date
    date_str = headers['date']

    gCon.log(f"date [{date_str}]")

    #date_str = date_str_kv.split("=")[1][1:-1]

    date_val = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')

    gCon.log(f"this is the date sent {date_val}")

    current_date = datetime.now()

    time_diff = current_date - date_val

    total_secs = abs(time_diff.total_seconds())

    gCon.log(f"this is the difference {time_diff}, secs {total_secs}")

    if (total_secs > 30):
        gCon.log("Too late!")
        return False

    # OK, digest and date are OK, now we check the signature.
    gCon.log(f"signature field is still {signature_field}")

    # first of all we build the signature string to validate
    host_hdr = headers['host']

    # OK, now I have to build the message to sign using the headers in the
    # order in which they have been signed in the source.

    # to verify the signature, I have to check the prefix
    #x_forwarded_prefix = ""

    if (hasattr(headers, 'x-forwarded-prefix') == True):
        x_forwarded_prefix = headers['x-forwarded-prefix']
        gCon.log(f"[yellow]1. c'è il prefisso! {x_forwarded_prefix}[/yellow]")
    else:
        gCon.log("[red]2. Non c'è il prefisso![/red]")

    try:
        x_forwarded_prefix = headers['x-forwarded-prefix']
        gCon.log(f"[yellow]1. c'è il prefisso! {x_forwarded_prefix}[/yellow]")
    except:
        gCon.log("[red]2. Non c'è il prefisso![/red]")
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

    gCon.rule("computed")
    gCon.log(f"This is my signature text computed\n|{signature_text}|")
    gCon.rule("computed end")


    #signature_text = b'(request-target): post %s\nhost: %s\ndate: %s\ndigest: SHA-256=%s\ncontent-type: %s' % (
    #        "/api/users/daemon/inbox".encode('utf-8'), 
    #        host_hdr.encode('utf-8'), 
    #        date_str.encode('utf-8'), 
    #        digest_body, 
    #        headers['content-type'].encode('utf-8'))

    #sign_utf8 = signature_text.decode('utf-8')

    #gCon.log(f"this is my signature block\n{sign_utf8}\n")
    signature_text = signature_text.encode('utf-8')

    remote_public_key = crypto_serialization.load_pem_public_key(
            pub_key_ob_pem.encode(),
            backend=crypto_default_backend()
    )

    gCon.log(f"I compare it to {signature_field}")

    try:
        remote_public_key.verify(
                base64.b64decode(signature_field),
                signature_text,
                padding.PKCS1v15(),
                hashes.SHA256()
                )
        gCon.log("[green]The signature is valid.[/green]")

    except Exception as err:
        gCon.log(f"[red]The signature is invalid.[/red]\n{err}")
        return False


    return True







# I take the raw request and this is the inbox
@app.post('/users/{username}/inbox')
async def user_inbox(username: str, request: Request):
    #print(username)

    if username != USER_ID:
        return Response(status_code=404)


    body = await request.body()
    body_str = body.decode()

    # Now I should get the actor field and schedule an echo.

    body_ob = json.loads(body_str)

    gCon.rule(" Start processing ")
    gCon.log(f"url {request.url} path {request.url.path} \
meth {request.method}")
    gCon.log(f"{request.headers}")


    # Here we check the body and signatures. Actually adelphos
    # uses only post methods inside the inbox as activities
    valid_ob = check_message(request, body_str, body_ob)

    if (valid_ob == False):
        return Response(status_code=401)


    actor_str = body_ob['actor']

    object_body = body_ob['object']

    if (isinstance(object_body, dict) == False):
        gCon.log(f"what is it? {str(object_body)}")
        return Response(status_code=400)

    content = object_body['content']

    clean_content = re.sub('<[^<]+?>', '', content) # type: ignore
 

    print (f"---------------- actor [{actor_str}]-------------------")
    print (f"Message: [{clean_content}]")
    print ("======================================== End")

    asyncio.create_task(send_echo(actor_str)) 

    return Response(status_code=202)


def main():

    instance_name = os.getenv(ADELPHOS_AP_ENV_KEY)
    if (instance_name is None):
        print(f"{ADELPHOS_AP_ENV_KEY} env var not defined, please provide it")
        sys.exit(1)

    load_conf(instance_name)

    # create the dao
    dao = AdelphosDao()

    gCon.log(f"the instance is {instance_name}, loading keys")

    port = get_config()['General']['port']
    key_file = get_config()['General']['private_key']
    HOST  = get_config()['General']['host']
    HOST_API = HOST + API_POINT
    load_keys(key_file)


    gCon.log(f"start here port {port}")
    gCon.log(f"{HOST}    host_api {HOST_API}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    typer.run(main)
