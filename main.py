import typer
from urllib.parse import urlparse
import sys
import base64
import datetime
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



    current_date = datetime.datetime.now().strftime(
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

    raw_signature = private_key.sign(
            signature_text,
            padding.PKCS1v15(),
            hashes.SHA256()
            )

    print(f"sender {sender_key}")
    signature_str = base64.b64encode(raw_signature).decode('utf-8') 
    print(f"signature {signature_str}")

    signature_header = f'keyId="{sender_key}",algorithm="rsa-sha256",headers="(request-target) digest host date",signature="{signature_str}"' 

    print(f"total {signature_header}")
    headers = {
            'Date': current_date,
            'Content-Type': 'application/activity+json',
            'Host': recipient_host,
            'Digest': "SHA-256="+digest.decode('utf-8'),
            'Signature': signature_header
            }


    r = requests.post(actor_inbox, headers=headers, 
                      json=follow_request_message)


    print(r)


######
# code to verify the signature and the digest.

def check_message(headers, body_str, body_ob):

    signature = headers['signature']

    gCon.log(f"signature {signature} {type(signature)}")

    # this is the global object, now we take the fields

    #keyId = signature['keyId']
    #signed_headers = signature['headers']
    #signature_val = signature['signature']

    (keyId, algorithm, signed_headers, signature_val) = signature.split(",")


    gCon.log(f"key id {keyId}")
    gCon.log(f"algorithm {algorithm}")
    gCon.log(f"signed headers {signed_headers}")
    gCon.log(f"signature_val {signature_val}")


    # Now we try to get the public key 
    key_id_val = keyId.split("=")[1][1:-1] #remove the quotes
    gCon.log(f"Get the public key {key_id_val}")

    headers = {"Accept" : "application/activity+json"}

    res_key = requests.get(key_id_val, headers = headers)

    gCon.log(f"this is the response {res_key}")

    if (res_key.status_code != 200):
        gCon.log()
        return False

    gCon.log(res_key.headers)

    key_ob_text = res_key.text

    gCon.log(f"[bold]{key_ob_text}[bold]")




    return True



######





# I take the raw request and this is the inbox
@app.post('/users/{username}/inbox')
async def user_inbox(username: str, request: Request):
    print(username)

    if username != USER_ID:
        return Response(status_code=400)


    body = await request.body()
    body_str = body.decode()

    # Now I should get the actor field and schedule an echo.

    body_ob = json.loads(body_str)

    # Here we check the body and signatures. Actually adelphos
    # uses only post methods inside the inbox as activities
    valid_ob = check_message(request.headers, body_str, body_ob)

    if (valid_ob == False):
        return Response(status_code=401)


    actor_str = body_ob['actor']

    object_body = body_ob['object']

    if (isinstance(object_body, dict) == False):
        gCon.log(f"what is it? {str(object_body)}")
        return Response(status_code=400)

    content = object_body['content']

    clean_content = re.sub('<[^<]+?>', '', content) # type: ignore
 

    print ("======================================== Start")
    gCon.log(f"{request.headers}")
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
