import typer
from urllib.parse import urlparse
import sys
import base64
from datetime import timedelta
from datetime import datetime

import json
import hashlib
import os
import uuid
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from typing import Union
import asyncio

from fastapi import FastAPI
import json
from fastapi import APIRouter, Request, Depends, Query, HTTPException, status, Response

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.logging import gCon
from app.config import load_conf
import uvicorn
import re
from app.api.RequestCtx import RequestCtx
from app.api.IngressGateway import ingress_request

from app.AdelphosApp import AdelphosApp, get_app
from app.consts import USER_ID
from app.consts import API_POINT
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse


# the app global object.
app = get_app()

# the web socket interface towards mastodon.



@app.get("/daemon_cli")
async def get():

    host = app.config['General']['host']
    host_api = host + API_POINT

    instance = app.instance

    html_string = f"""
<!DOCTYPE html>
<html>
    <head>
    <title>Welcome to adelphos instance {instance} @ {host}</title>
    </head>
    <body>
        <h1>Adelphos daemon for instance: {instance} @ host {host}</h1>
        <form action="" onsubmit="sendMessage(event)">
        <label>Security Token: <input type="text" id="token" autocomplete="off" value=""/></label>
        <hr>
        <input type="text" id="messageText" autocomplete="off"/>
        <button>Send</button>
        </form>
        <ul id='messages'>
        <li>Adelphos: login with command 'login alias password' to receive OTP token</li>
        </ul>
        <script>
            var ws = new WebSocket("wss://{host_api}/ws");"""

    # here we have to change the string without the formatting because it
    # has the { parenthesis
    html_string += """
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.insertBefore(message, messages.firstChild)
            };
            function sendMessage(event) {
                var token = document.getElementById('token')
                var input = document.getElementById("messageText")
                input += " tk " + token.value
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

    gCon.log(f"Hello I give to you the html")
    return HTMLResponse(html_string)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    #client = await websocket.accept()
    client = await app.conn_hndl.accept(websocket)

    # this is the never ending cycle.
    await client.serve()


@app.get("/.well-known/webfinger",
    description="Adelphos's end point",
)
async def webfinger(resource: str = Query(..., alias="resource")):

    #global HOST
    host = app.config['General']['host']
    host_api = host + API_POINT

    gCon.log(f"[red]webfinger[/red] host {host} resource {resource}")

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
async def user(username : str):

    gCon.log(f"[red]get {username}[/red]")

    if username != USER_ID:
        return Response(status_code=404)

    host = app.config['General']['host']
    host_api = host + API_POINT

    instance = app.instance

    response_ob = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
        ],
        "id": f"https://{host_api}/users/{USER_ID}",
        "inbox": f"https://{host_api}/users/{USER_ID}/inbox",
        "outbox": f"https://{host_api}/users/{USER_ID}/outbox",
        "type": "Person",
        "name": f"Adelphos' daemon for instance {instance} @ {host}",
        "preferredUsername": USER_ID,
        "publicKey": {
            "id": f"https://{host_api}/users/{USER_ID}#main-key",
            "owner": f"https://{host_api}/users/{USER_ID}",
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

    gCon.log(f"[red]post inbox {username}[/red]")

    res_code = 404
    if username == USER_ID:

        ctx = RequestCtx(app, request)

        ctx.body = await ctx.request.body()

        res_code = await ingress_request(ctx)
        
    return Response(status_code = res_code)



def main():

    port = app.config['General']['port']
    gCon.log(f"Will start with port {port}")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    typer.run(main)
