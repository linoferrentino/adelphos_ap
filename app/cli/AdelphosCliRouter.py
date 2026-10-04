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
import re

from app.cli.CliRouter import CliRouter
from app.logging import gCon

from starlette.websockets import WebSocket
from starlette.routing import Route
from starlette.routing import WebSocketRoute
from starlette.responses import HTMLResponse

from app.sdc.Dependencies import Dependencies


class AdelphosCliRouter(CliRouter):

    def __init__(self, kernel):
        super().__init__(kernel)


    async def in_daemon_cli(self, request):
        config = self.conf

        host = config.get_host()
        host_api = host + config.get_root_path() 

        if config.is_localhost():
            wsock_schema = "ws"
        else:
            wsock_schema = "wss"

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
        <title>Chat with adelphos instance {instance} running on host {host}</title>
        </head>
        <body>
            <h1>Adelphos instance: {instance}, running on host {host} ver {CNST.VERSION}</h1><br>
            <h3>&copy; 2026 Lino Ferrentino
            &lt;lino.ferrentino@gmail.com&gt;. This is free Software
            licenced with GPL3</h3>
    <div class="chat-container" id="chat">
        <div class="message received">

        <p>Welcome to the Command Line Interface to the Adelphos Instance {instance}@{host}

        <p>
        Adelphos uses a Mastodon instance (or a similar software which
        speaks the Ativity Pub protocol) to authenticate users.

        <p>

        Please refer to the reference manual located on <a
        href="https://{host}">Documentation</a>

        <p>
        </div>
        <div class="message received">
        <h1>Quick start</h1>

        <p>

        If you have an alias on this instance you can type the command
        <pre>alias.login alias $alias.$family password $password</pre> to receive the OTP token.

        <p>
        If you haven't yet created an alias send a message to me from your
        Mastodon account to create one.

        <p>

        The message should be a private mention
        to the @{CNST.DAEMON_ID} user at this instance. Refer to your social
        software documentation, but usually you should type a message like this:

        <p>
        <pre>
        @{CNST.DAEMON_ID}@{host} alias.create alias $name.$family password $password
        </pre>

        <p>
        If the alias is well formed and the family does not exist yet on
        this instance you will receive shortly a success message from me and you
        can come back here to login.
        <p>

        <p>

        </div>

        <div class="message received">
        Copyright &copy; 2026 Lino Ferrentino &lt;lino.ferrentino@gmail.com&gt;
        
        <p>

        This program comes with <b>ABSOLUTELY NO WARRANTY</b>

        <p>
        This is free software, and you are welcome to redistribute it on
        the terms of the General Public Licence Version 3. You can find the
        full text <a
        href="https://www.gnu.org/licenses/gpl-3.0.html">here</a>
        <p>
        You can view the
        source code of adelphos <a href="https://github.com/linoferrentino/adelphos_ap">here</a>
        </div>
    </div>

    <div class="input-container">
        <input type="text" id="messageInput" placeholder="Type a message...">
        <button onclick="sendMessage()">Send</button>
    </div>

          <script>

                var ws = new WebSocket("{wsock_schema}://{host_api}/ws");"""

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
        cli_handler = self.get_dep(Dependencies.CLI_HANDLER)
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
