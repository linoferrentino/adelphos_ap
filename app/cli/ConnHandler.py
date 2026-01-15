# 
# The class that manages the connections.
#
# 
# 
# 

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websockets.asyncio.server import broadcast
from app.logging import gCon
from app.api.Dispatcher import send_msg_to_alias
from app.api.params import make_cmd_params
import asyncio


# the class that holds the data relative to a client
# this holds a session state for the socket.
class WebSocketContext:

    def __init__(self, app, websocket):
        # at first there is not a login.
        self.actor = None
        pass

def login_required(func):

    def check_login(ctx):
        return func(ctx)

    return check_login


async def login_hndl_ws(wsctx):
    pass


@login_required
async def login_hndl_ws(wsctx):
    pass


# these are the commands recognized by the web socket.
ws_cmd_handlers = {
        "create_group": create_group_hndl,
        "login" : login_hndl,
}



# this is the client that will do the cycle to process the messages
class ClientWs:


    def __init__(self, app, websocket):
        self.wsctx = WebSocketContext()
        self.wsctx.app = app
        self.websocket = websocket
        self.running = True
        # this is a one pad token which the user is asked to give.
        self.token = None


    async def web_socket_parse(self):
        pass


    async def _internal_serve(self):

        while True:
            try:

                data = await asyncio.wait_for(
                    self.websocket.receive_text(), 10)

            except asyncio.TimeoutError:
                #data = "are you still there?"
                continue

            self.wsctx.cmd_splits = data.split()
            self.wsctx.cmd = data.pop(0)
            make_cmd_params(wsctx)
            gCon.log(f"received {data} command is {self.wsctx.cmd}")

            if (self.wsctx.actor is None):
                # no login
                pass

            answer = await send_msg_to_alias(self.wsctx)
            await self.websocket.send_text(f"remote answers {answer}")


    async def serve(self):
        try:

            await self._internal_serve()

        except WebSocketDisconnect as wds:

            # this is called. No problem
            gCon.log("disconnect")

            # this client will be garbage collected later.
            self.running = False


    async def stop(self):
        if (self.running == False):
            return
    
        await self.websocket.close()


# this object will accept the web sockets and do a garbage collect when
# they are dead or inactive for a certain period of time
class ConnHandler:


    def __init__(self, app):
        # this is the list of all clients connected.
        self.clients = []
        self.app = app


    async def accept(self, websocket):

        await websocket.accept()
        client = ClientWs(self.app, websocket)
        self.clients.append(client)
        return client

    
    async def stop(self):

        gCon.log("I will close the connections")
        #wslist = [ ws.websocket for ws in self.clients]
        #broadcast(wslist, "The server is going dow NOW!")

        #for ws in self.clients:
            #await ws.websocket.send_text(f"System is going down!")
            #await ws.stop()

