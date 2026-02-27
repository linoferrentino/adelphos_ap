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
from app.api.IngressGateway import ActivityPubGateway
from app.api.IngressGateway import _ingress_request
import uvicorn
import re
from app.api.RequestCtx import RequestCtx
#from app.api.IngressGateway import ingress_request

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

    html_string = """
<!DOCTYPE html>
<html>

<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #8a8a8a;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        height: 100vh;
    }

    /* Chat container */
    .chat-container {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        padding: 10px;
        overflow-y: scroll;
        scrollbar-width: thin; /* Firefox */
        scrollbar-color: #888 #f2f2f2; /* Firefox */
    }


    /* Custom scrollbar for WebKit browsers */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: #f2f2f2;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background-color: #888;
        border-radius: 4px;
    }
    .chat-container::-webkit-scrollbar-thumb:hover {
        background-color: #555;
    }

    /* Message bubbles */
    .message {
        max-width: 70%;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 15px;
        line-height: 1.4;
        word-wrap: break-word;
    }

    .sent {
        background-color: #4CAF50;
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 0;
    }

    .received {
        background-color: #e0e0e0;
        color: black;
        align-self: flex-start;
        border-bottom-left-radius: 0;
    }

    /* Input area */
    .input-container {
        display: flex;
        padding: 10px;
        background-color: white;
        border-top: 1px solid #ccc;
    }

    .input-container input {
        flex: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 20px;
        outline: none;
    }

    .input-container button {
        margin-left: 10px;
        padding: 10px 15px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 20px;
        cursor: pointer;
    }

    .input-container button:hover {
        background-color: #45a049;
    }
</style>

"""

    html_string += f"""
    <head>
    <title>Welcome to adelphos instance {instance} @ {host}</title>
    </head>
    <body>
        <h1>Adelphos instance: {instance}</h1><br><h2>{USER_ID}@{host}</h2>

<div class="chat-container" id="chat">
    <div class="message received">

    <p>
    Hello, here is the daemon listening.
    <p>

    If you have already created an alias on this instance login with command 'login alias ##$alias.$family password $password' to receive OTP token.

    <p>
    If you haven't yet created an alias send a message to me from your
    Mastodon account to create one. The message should be a private mention
    to the @daemon user at this instance. Like this:

    <p>
    @daemon@{host} alias_create alias ##<name>.<family> password <password>

    <p>
    After that come here to login.
    <p>

    </div>
</div>

<div class="input-container">
    <input type="text" id="messageInput" placeholder="Type a message...">
    <button onclick="sendMessage()">Send</button>
</div>

      <script>


            var ws = new WebSocket("wss://{host_api}/ws");"""

    # here we have to change the string without the formatting because it
    # has the { parenthesis
    html_string += """


document.getElementById('messageInput').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });


            ws.onmessage = function(event) {
                const chat = document.getElementById("chat");
                const msg = document.createElement('div');
                msg.classList.add('message', 'received');
                msg.textContent = event.data
                chat.appendChild(msg)
                chat.scrollTop = chat.scrollHeight;

            };
            function sendMessage(event) {
                //var token = document.getElementById('token');
                var input = document.getElementById("messageInput");
                /*
                if (token.value != "") {
                    msg_total = input.value + " tk " + token.value;
                } else {
                }
                */
                msg_total = input.value;
                //console.log("writing " + msg_total)
                ws.send(msg_total);

                msg_logged = msg_total.replace(/password .*/, "password XXX")
                msg_logged = msg_logged.replace(/token .*/, "token XXX")


                const chat = document.getElementById("chat");
                const msg = document.createElement('div');
                msg.classList.add('message', 'sent');
                msg.textContent = msg_logged;
                chat.appendChild(msg)
                input.value = '';
                chat.scrollTop = chat.scrollHeight;
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
    await client.serve_forever()


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
        "type": "Bot",
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


# this is the entry point for the daemon in Activity Pub.
# We support only one user.
# the other users are only aliases of Mastodon users which enroll here.
@app.post('/users/{username}/inbox')
async def user_inbox(username: str, request: Request):

    gCon.log(f"[red]post inbox {username}[/red]")

    res_code = 404
    if username == USER_ID:

        # I create the Activity Pub Gateway
        #gateway = RequestCtx(app, request)
        #(res_code, content) = await _ingress_request(gateway)
        
        gateway = ActivityPubGateway(app)

        # this will return the return code and will process the request asynchronously
        res_code = await gateway.new_request(request)


        # the result code is given immediately, but the message is processed
        # asynchronously
        #res_code = await gateway.accept(request)
        
    return Response(status_code = res_code)


def main():

    port = app.config['General']['port']
    gCon.log(f"Will start with port {port}")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    typer.run(main)
