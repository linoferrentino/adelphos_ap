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

#from app.keys import load_keys, public_key, private_key
from app.logging import gCon
from app.config import load_conf
#from app.config import get_config
from app.dao.AdelphosDao import AdelphosDao
import uvicorn
import re
from app.api.RequestCtx import RequestCtx
from app.api.IngressGateway import ingress_request

from app.AdelphosApp import AdelphosApp, get_app
from app.consts import USER_ID
from app.consts import API_POINT


# the app global object.
app = get_app()


@app.get("/.well-known/webfinger",
    description="Adelphos's end point",
)
def webfinger(resource: str = Query(..., alias="resource")):

    #global HOST
    host = app.config['General']['host']
    host_api = host + API_POINT

    print(f"------- host {host} resource {resource}")

    if resource != f"acct:{USER_ID}@{host}":
        return Response(status_code=404)

    response = Response(
        content=json.dumps({
            "subject": f"acct:{USER_ID}@{host}",
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"https://{host_api}/users/{USER_ID}"
                }
            ]
        })
    )
    
    response.headers['Content-Type'] = 'application/jrd+json'
    
    return response


@app.get('/users/{username}')
def user(username : str):

    if username != USER_ID:
        return Response(status_code=404)

    host = app.config['General']['host']
    host_api = host + API_POINT

    response_ob = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
        ],
        "id": f"https://{host_api}/users/{USER_ID}",
        "inbox": f"https://{host_api}/users/{USER_ID}/inbox",
        "outbox": f"https://{host_api}/users/{USER_ID}/outbox",
        "type": "Person",
        "name": "Adelphos' activity pub daemon",
        "preferredUsername": "daemon",
        "publicKey": {
            "id": f"https://{host_api}/users/{USER_ID}#main-key",
            "id": f"https://{host_api}/users/{USER_ID}",
            "publicKeyPem": app.public_key
        }
    }

    resp_json = jsonable_encoder(response_ob)

    response = JSONResponse(content = resp_json)

    response.headers['Content-Type'] = 'application/activity+json'

    return response


# I take the raw request and this is the inbox
@app.post('/users/{username}/inbox')
async def user_inbox(username: str, request: Request):

    res_code = 404
    if username == USER_ID:

        ctx = RequestCtx(app, request)

        ctx.body = await ctx.request.body()

        res_code = ingress_request(ctx)
        
    return Response(status_code = res_code)



def main():

    port = app.config['General']['port']
    gCon.log(f"Will start with port {port}")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    typer.run(main)
