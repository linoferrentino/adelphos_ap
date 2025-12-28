# this is the ingress gateway.

# this is called synchronously.
from app.consts import USER_ID
from app.logging import gCon
from app.api.Dispatcher import dispatch_request
import requests
import base64
import json
import re
import hashlib
from datetime import datetime
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import asyncio



def check_message(ctx):

    request = ctx.request
    body_str = ctx.body_str
    body_ob = ctx.body_ob

    headers = request.headers

    signature = headers['signature']

    # this is the global object, now we take the fields
    (keyId, algorithm, signed_headers, signature_val) = signature.split(",")

    # transform the string into a list.
    signed_headers_list = signed_headers.split("=")[1][1:-1].split(" ")
    signature_field_list = signature_val.split("=", 1)
    signature_field_raw = signature_field_list[1]
    signature_field = signature_field_raw[1:-1]

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

    if (res_key.status_code != 200):
        gCon.log(f"Could not fetch the public key {res_key.status_code}")
        return False

    key_ob_text = res_key.text

    ctx.key_ob = json.loads(key_ob_text)

    gCon.log(f"this is the actor {ctx.key_ob}")

    pub_key_ob = ctx.key_ob['publicKey']

    pub_key_ob_id = pub_key_ob['id']
    pub_key_ob_pem = pub_key_ob['publicKeyPem']

    #gCon.log(f"obtained id {pub_key_ob_id}")

    # are they the same?
    if (pub_key_ob_id != key_id_val):
        gCon.log("Error, got another key")
        return False

    # is the owner?
    if (pub_key_ob['owner'] != ctx.actor_str):
        gCon.log("Error, owner different")
        return False

    ####### 1st, Check the digest
    digest_body = base64.b64encode(hashlib.sha256(
        body_str.encode('utf-8')).digest())

    digest_body_total = "SHA-256=" + digest_body.decode('utf-8')

    #gCon.log(f"I expect {digest_body_total} as digest in headers")

    digest_sign = headers['digest']

    #gCon.log(f"I got {digest_sign} as digest in headers")

    if (digest_body_total != digest_sign):
        gCon.log("digest mismatch, go away")
        return False

    ####### 2nd check date
    date_str = headers['date']

    gCon.log(f"date [{date_str}]")

    #date_str = date_str_kv.split("=")[1][1:-1]

    date_val = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')

    #gCon.log(f"this is the date sent {date_val}")

    current_date = datetime.now()

    time_diff = current_date - date_val

    total_secs = abs(time_diff.total_seconds())

    #gCon.log(f"this is the difference {time_diff}, secs {total_secs}")

    if (total_secs > 30):
        gCon.log("Too late!")
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

    signature_text_bin = signature_text.encode('utf-8')

    remote_public_key = crypto_serialization.load_pem_public_key(
            pub_key_ob_pem.encode(),
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


def ingress_request(ctx) -> int:

    # I accept messages only for the daemon
    #if ctx.username != USER_ID:
    #    return 404

    ctx.body_str = ctx.body.decode()
    # I create the request context and pass it to the dispatcher


    # Now I should get the actor field and take the alias from the db, if
    # present, otherwise I assume that this is a create activity

    ctx.body_ob = json.loads(ctx.body_str)
    ctx.actor_str = ctx.body_ob['actor']

    gCon.rule(f"Start processing from {ctx.actor_str}")
    gCon.log(f"For: url {ctx.request.url}")

    ctx.object_body = ctx.body_ob['object']

    if (isinstance(ctx.object_body, dict) == False):
        gCon.log(f"what is it? {str(ctx.object_body)}")
        return 400

    content = ctx.object_body['content']

    # remove HTML tags
    ctx.clean_content = re.sub('<[^<]+?>', '', content) 

    gCon.log(f"Message: [yellow]{ctx.clean_content}[/yellow]")

    ob_type = ctx.body_ob['type']

    # I only understand activity create post objects.
    if (ob_type != 'Create'):
        gCon.log(f"Unrecognized activity type {ob_type}")
        return 400

    object_body_type = ctx.object_body['type']
    if (object_body_type != 'Note'):
        gCon.log(f"Unrecognized object internal type {object_body_type}")
        return 400

    valid_ob = check_message(ctx)

    if (valid_ob == False):
        return 401
    
    asyncio.create_task(dispatch_request(ctx)) 

    # the message has been accepted, I will return the response after.
    return 202

