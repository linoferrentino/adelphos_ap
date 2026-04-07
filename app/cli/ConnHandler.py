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
# The class that manages the connections.
import asyncio
import traceback
from datetime import datetime

from fastapi import APIRouter, FastAPI, WebSocket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from websockets.asyncio.server import broadcast

from app.api.AdelphosException import AdelphosException
from app.api.AliasApi import AliasApi
from app.api.WebSocketGateway import WebSocketGateway
from app.cli.CliProvider import CliProvider
from app.dao.AdelphosUri import uriparse
from app.dao.AliasDto import AliasDto
from app.logging import gCon
from app.transport.SyncRouter import SyncRouter

def login_required(func):

    def check_login(ctx):
        # I have to make sure that the user is logged.
        if (ctx.alias_api.is_logged_in() == False):
            raise AdelphosException("You have to login, first")
        return func(ctx)

    return check_login


async def token_hndl_ws(ctx):
    token = ctx.get_param_safe('tk')

    # this is local function, no need to await
    msg = ctx.alias_api.recv_token(token)

    return msg


async def login_hndl_ws(ctx):

    # If you already have a login what are you doing?
    if (ctx.alias_api.is_logged_in()):
        raise AdelphosException("You already have logged in (logout first!)")

    alias = ctx.get_param_safe('alias')
    password = ctx.get_param_safe('password')

    # now I have to parse the uri, the alias is *always* in a format like
    # ##name.family or #ad#name.family@...
    alias_uri = uriparse(alias)

    gCon.log(f"You {alias_uri} want to login!")

    # let's suppose that we want to login, first of all we create
    # an AliasApi and we pass the message
    #ctx.alias_api = AliasApi(alias_uri)
    msg = await ctx.alias_api.login(alias_uri, password)

    return msg


async def create_group_hndl(ctx):
    pass


# the create trust line is a initiator command which begins with an alias
@login_required
async def tl_create_handler(ctx):

    # a simple pass message, after I have checked the login.
    self.tl_api.create()

    #alias_to = get_param_safe(ctx, 'alias_to')

    ## first of all I have to get the actor from the alias.
    ## the alias must be local.
    #ctx.alias_from = AliasDao.get_from_uri(ctx, alias_from)
    #if (ctx.alias_ob is None):
    #    raise AdelphosException(f"unknown alias {alias_from}")

    ## does the alias belong to the user?
    #if (ctx.alias_from.actor_fk != ctx.actor.actor_id):
    #    raise AdelphosException(
    #            f"The alias {alias_from} does not belong to you.")

    ## OK, now for the outer alias.
    #if (alias_to[0] == '$'):
    #    # this is a remote alias.
    #    raise AdelphosException(f"implementation to remote alias to do")


    ## this is a local alias, so I can create here the trust line, but
    ## only if the other alias agrees.
    #post_message_to_other_alias(ctx, "do you really want?")
    #

    ## I have to parse the alias to.
    #return f"create trust line to {alias_to} initiated, waiting for confirmation"


# these are the commands recognized by the web socket.
ws_cmd_handlers = {
        "create_group": create_group_hndl,
        "login" : login_hndl_ws,
        "put_token" : token_hndl_ws,
        "tl_create": tl_create_handler,
}


# this is the client that will do the cycle to process the messages
class ClientWs:


    def __init__(self, app, websocket):
        self.ctx = WebSocketGateway(app, websocket)
        self.websocket = websocket
        self.running = True


    async def _internal_serve(self):

        while True:
            try:

                data = await asyncio.wait_for(
                    self.websocket.receive_text(), 10)

            except asyncio.TimeoutError:
                #data = "are you still there?"
                continue

            #gCon.log(f"received ]{data}[")

            #await self._handle_cmdline(data)
            # I handle it to the gateway
            await self.ctx.new_request(data)


    # this is the never ending loop which goes away only if the client
    # disconnects.
    async def serve_forever(self):

        while True:
            try:

                await self.serve_a_cycle()
                # If I am here, I just continue
                continue

            except WebSocketDisconnect as wds:
                # No problem, come another time
                #gCon.log("disconnect")
                pass

            # this to catch all other errors, these are bugs :(
            except Exception as ex:
                traceback.print_exc()
                await self.websocket.send_text(f"Server error, we apologize.")

            # if I arrive here there has been a problem, go away, the system
            # might be in a bad state.
            break

        self.running = False


    async def serve_a_cycle(self):

        try:

            await self._internal_serve()

        except AdelphosException as err:

            # this is a "benign" error, we eat the exception and continue
            await self.websocket.send_text(f"Error: {err}")


    async def stop(self):
        if (self.running == False):
            return
    
        await self.websocket.close()


class WebSocketRouter(APIRouter):

    def __init__(self, wshndl):
        super().__init__()

        @self.get("/daemon_cli")
        async def daemon_cli_inner():
            return await wshndl.daemon_cli()
   

        @self.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            client = await wshndl.accept(websocket)
            await client.serve_forever()


# this is a synchronous router, used to dispactch method calls
class WebSocketSyncRouter(SyncRouter):


    def __init__(self, wshndl):
        super().__init__()
        super()._register_route('accept', wshndl.sync_accept)



# this object will accept the web sockets and do a garbage collect when
# they are dead or inactive for a certain period of time
class ConnHandler(CliProvider):


    # TODO remove the dependency on the app
    def __init__(self, app):
        self.clients = []
        self.app = app


    # gets the router relative to the web sockets.
    def get_async_router(self):
        router = WebSocketRouter(self)
        return router


    def get_sync_router(self):
        router = WebSocketSyncRouter(self)
        return router


    async def accept(self, websocket):

        await websocket.accept()
        client = ClientWs(self.app, websocket)
        self.clients.append(client)
        return client

    
    async def stop(self):
        pass

        #gCon.log("I will close the connections")
        #wslist = [ ws.websocket for ws in self.clients]
        #broadcast(wslist, "The server is going dow NOW!")

        #for ws in self.clients:
            #await ws.websocket.send_text(f"System is going down!")
            #await ws.stop()


    # It gives the page into which we can type the commands.
    async def daemon_cli(self):
        host = self.app.config['General']['host']
        host_api = host + API_POINT

        instance = self.app.instance

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


