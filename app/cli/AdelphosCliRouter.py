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

import app.consts as CNST

from app.cli.CliRouter import CliRouter
from app.logging import gCon

from starlette.websockets import WebSocket
from starlette.routing import Route
from starlette.routing import WebSocketRoute

#import app.sdc.s_utils as sdc
from app.sdc.Dependencies import Dependencies


class AdelphosCliRouter(CliRouter):

    def __init__(self, vhost):
       self.vhost = vhost 

    async def in_daemon_cli(self, request):
        config = self.vhost.get_dep(Dependencies.CONFIG)

        #host = self.vhost.config['General']['host']
        host = config.get_host()
        host_api = host + CNST.API_POINT

        #instance = self.vhost.instance_name
        instance = config.get_instance()

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
        #gCon.log(f"A+SSSSSSSS {self}")
        cli_handler = self.vhost.get_dep(Dependencies.CLI_HANDLER)
        #gCon.log(f"A+SSSSSSSS {cli_handler}")

        if cli_handler is not None:
            await cli_handler.serve_forever(websocket)
        else:
            await websocket.accept()
            await websocket.send_text(f"No cli available")
            await websocket.close()


    def get_cli_routes(self):
        routes = [
                Route(CNST.DAEMON_CLI_ROUTE, self.in_daemon_cli, methods=['GET']),
                WebSocketRoute(CNST.WS_ROUTE, self.in_websocket),
                ]
        return routes
