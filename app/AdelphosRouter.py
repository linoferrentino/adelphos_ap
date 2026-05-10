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
# the router for our application.

#from fastapi import APIRouter, FastAPI, WebSocket
#import typer
#from urllib.parse import urlparse
#import sys
#import base64
#from datetime import timedelta
#from datetime import datetime
#
#import json
#import hashlib
#import os
#import uuid
#from cryptography.hazmat.backends import default_backend as crypto_default_backend
#from cryptography.hazmat.primitives import serialization as crypto_serialization
#from cryptography.hazmat.primitives import hashes
#from cryptography.hazmat.primitives.asymmetric import padding
#from typing import Union
#import asyncio
#
#from fastapi import FastAPI
#import json
#from fastapi import APIRouter, Request, Depends, Query, HTTPException, status, Response
#
#from fastapi.encoders import jsonable_encoder
#from fastapi.responses import JSONResponse
#
#from app.logging import gCon
#from app.config import load_conf
##from app.ap_api.ActivityPubGateway import ActivityPubGateway
#import uvicorn
#import re
#
##from app.AdelphosApp import AdelphosApp, get_app
#from app.consts import DAEMON_ID 
#from app.consts import API_POINT
#from fastapi import FastAPI, WebSocket
#from fastapi.responses import HTMLResponse
#

import re
import json

from starlette.routing import Route
from starlette.routing import WebSocketRoute
from starlette.responses import Response
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket

import app.consts as CNST
from app.logging import gCon

from app.transport.Routable import Routable
from app.endpoints.AdelphosDaemonCli import AdelphosDaemonCli
from app.endpoints.AdelphosWebSocket import AdelphosWebSocket
from app.federation.SocialProvider import SocialProvider



class AdelphosRouter(Routable):


    def __init__(self, instance_name, config, social : SocialProvider = None):
        self.instance_name = instance_name
        self.config = config
        self.social = social


    async def in_webfinger(self, request):
        resource = request.query_params.get('resource')
        if resource is None:
            return Response(status_code = 401)
        
        ap_user_match = re.match('acct:(.*?)@(.*)$', resource[0])
        if (ap_user_match is None):
            return Response(status_code=401)

        ap_user_rex = ap_user_match.group(1)
        if (self.social.local_user_exists(ap_user_rex) == False):
            return Response(status_code=404)

        host = self.config[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]
        host_api = f"{host}/{CNST.API_POINT}"

        response = Response(
            content=json.dumps({
                "subject": resource,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/activity+json",
                        "href": f"https://{host_api}/users/{ap_user_rex}"
                    }
                ]
            })
        )
        
        response.headers['Content-Type'] = 'application/jrd+json'
        return response


    async def in_infouser(self, request):
        pass


    async def in_inbox(self, request):
        pass


    async def in_daemon_cli(self, request):

        host = self.config['General']['host']
        host_api = host + CNST.API_POINT

        instance = self.instance_name

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
            <h1>Adelphos instance: {instance}</h1><br><h2>{CNST.DAEMON_ID}@{host}</h2>

    <div class="chat-container" id="chat">
        <div class="message received">

        <p>
        Hello from the adelphos daemon running @{host}!
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

###################################### NEW 


                #var ws = new WebSocket("wss://{host_api}/ws");
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
                    var input = document.getElementById("messageInput");
                    msg_total = input.value;
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
        return HTMLResponse(html_string)


    async def in_websocket(self, websocket: WebSocket):
        await websocket.accept()
        text = await websocket.receive_text()
        await websocket.send_text(f"Hello, world! {text}")
        await websocket.close()


    def get_routes(self):
        routes = [
                Route(CNST.WEBFINGER_ROUTE,
                      endpoint = self.in_webfinger, methods=['GET']),
                Route(CNST.USER_DISCOVER_ROUTE, 
                      endpoint = self.in_infouser, methods=['GET']),
                Route(CNST.USER_INBOX_ROUTE,
                      endpoint = self.in_inbox, methods=['POST']),
                Route(CNST.DAEMON_CLI_ROUTE, self.in_daemon_cli, methods=['GET']),
                WebSocketRoute(CNST.WS_ROUTE, self.in_websocket),
                ]
        return routes


    async def init_up(self):
        pass


    async def tear_down(self):
        pass


# I initialize the router with the app.
#class AdelphosRouter_deprecated(APIRouter):
class AdelphosRouter_deprecated():


    def __init__(self, app):
        super().__init__()
        self.app = app


    # It gives the page into which we can type the commands.
    async def daemon_cli(self, app):
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
            <h1>Adelphos instance: {instance}</h1><br><h2>{DAEMON_ID}@{host}</h2>

    <div class="chat-container" id="chat">
        <div class="message received">

        <p>
        Hello from the adelphos daemon running @{host}!
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


                var ws = new WebSocket("wss://{host}/ws");"""

                ##################### OLD OLD OLD OLD

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
                    var input = document.getElementById("messageInput");
                    msg_total = input.value;
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
        return HTMLResponse(html_string)


def make_router(app):

    router = AdelphosRouter(app)

    test_instance = app.is_test_instance()

    if test_instance:
        # I can add a backdoor to test the application (in testing).
        @router.post('/_backdoor_api_/{cmd}')
        async def _backdoor_api(cmd: str, request : Request):
            body = await request.body()
            body_str = body.decode()
            body_ob = json.loads(body_str)
            ap_mock = app.get_ap_mockup()
            # the mock might as well do other async calls
            res = await ap_mock.proc_cmd(cmd, body_ob)
            #gCon.log(f"===================================== {res}")
            return { 'res' : res }


    @router.get("/daemon_cli")
    async def daemon_cli_inner():
        return await router.daemon_cli(app)
   

    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        client = await app.conn_hndl.accept(websocket)
        await client.serve_forever()


    @router.get("/.well-known/webfinger",
        description="Adelphos's end point",
    )
    async def webfinger(resource: str = Query(..., alias="resource")):

        host = app.config['General']['host']
        host_api = host + API_POINT

        #gCon.log(f"[red]webfinger[/red] host {host} resource {resource}")

        ap_user_match = re.match('acct:(.*?)@(.*)$', resource)
        if (ap_user_match is None):
            return Response(status_code=401)

        host_rex = ap_user_match.group(2)
        if (host_rex != host):
            return Response(status_code=404)

        ap_user_rex = ap_user_match.group(1)
        if (app.ap_user_exists(ap_user_rex) == False):
            return Response(status_code=404)

        response = Response(
            content=json.dumps({
                "subject": resource,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/activity+json",
                        "href": f"https://{host_api}/users/{ap_user_rex}"
                    }
                ]
            })
        )
        
        response.headers['Content-Type'] = 'application/jrd+json'
        return response


    @router.get('/users/{username}')
    async def user(username : str):

        #gCon.log(f"[red]GET {username}[/red]")

        user_info = app.ap_user_info(username)
        if (user_info is None):
            return Response(status_code=404)

        host = app.config['General']['host']
        host_api = host + API_POINT

        instance = app.instance

        response_ob = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": f"https://{host_api}/users/{username}",
            "inbox": f"https://{host_api}/users/{username}/inbox",
            "outbox": f"https://{host_api}/users/{username}/outbox",
            "type": user_info[0],
            "name": user_info[2],
            "preferredUsername": user_info[1],
            "publicKey": {
                "id": f"https://{host_api}/users/{username}#main-key",
                "owner": f"https://{host_api}/users/{username}",
                "publicKeyPem": app.public_key
            }
        }

        resp_json = jsonable_encoder(response_ob)
        response = JSONResponse(content = resp_json)
        response.headers['Content-Type'] = 'application/activity+json'
        return response


    @router.post('/users/{username}/inbox')
    async def user_inbox(username: str, request: Request):

        #gCon.log(f"[red]post inbox {username}[/red]")

        res_code = 404
        if username == DAEMON_ID:

            # this will return the return code and will process the request asynchronously
            res_code = await app.ap_gateway.new_request(request)

        elif test_instance:

            # the message is not for the daemon, it might be for some test users
            # that I have .
            res_code = await app.ap_mockup.new_request(request)
            
        return Response(status_code = res_code)


    return router


