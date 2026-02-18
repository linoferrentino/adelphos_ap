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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websockets.asyncio.server import broadcast
from app.logging import gCon
from app.api.AdelphosException import AdelphosException
from app.api.Dispatcher import send_msg_to_local_alias
from app.api.params import make_cmd_params
from app.api.AppCtx import WebSocketContext
from app.dao.AliasDto import AliasDto
from app.api.params import get_param_safe
from app.dao.AdelphosUri import uriparse
from app.api.AliasApi import AliasApi
import asyncio
import traceback



def login_required(func):

    def check_login(ctx):
        return func(ctx)

    return check_login


async def login_hndl_ws(wsctx):
    pass


@login_required
async def login_hndl_ws(wsctx):
    pass


async def create_group_hndl(wsctx):
    pass


async def tl_create_handler(ctx):
    alias_from = get_param_safe(ctx, 'alias_from')
    alias_to = get_param_safe(ctx, 'alias_to')
    trust = get_param_safe(ctx, 'trust')

    # first of all I have to get the actor from the alias.
    # the alias must be local.
    ctx.alias_from = AliasDao.get_from_uri(ctx, alias_from)
    if (ctx.alias_ob is None):
        raise AdelphosException(f"unknown alias {alias_from}")

    # does the alias belong to the user?
    if (ctx.alias_from.actor_fk != ctx.actor.actor_id):
        raise AdelphosException(
                f"The alias {alias_from} does not belong to you.")

    # OK, now for the outer alias.
    if (alias_to[0] == '$'):
        # this is a remote alias.
        raise AdelphosException(f"implementation to remote alias to do")


    # this is a local alias, so I can create here the trust line, but
    # only if the other alias agrees.
    post_message_to_other_alias(ctx, "do you really want?")
    

    # I have to parse the alias to.

    # remove the dollar.
    #alias_to = alias_to[1:]

    return f"create trust line to {alias_to} initiated, waiting for confirmation"


# these are the commands recognized by the web socket.
ws_cmd_handlers = {
        "create_group": create_group_hndl,
        "login" : login_hndl_ws,
        "tl_create": tl_create_handler,
}


# this is the client that will do the cycle to process the messages
class ClientWs:


    def __init__(self, app, websocket):
        self.wsctx = WebSocketContext(app, websocket)
        self.websocket = websocket
        self.running = True


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

            gCon.log(f"received {data} command")

            self.wsctx.cmd_splits = data.split()
            self.wsctx.cmd = self.wsctx.cmd_splits.pop(0)
            make_cmd_params(self.wsctx)

            alias = get_param_safe(self.wsctx, 'alias')
            password = get_param_safe(self.wsctx, 'password')

            # now I have to parse the uri, the alias is *always* in a format like
            # ##name.family or #ad#name.family@...
            alias_uri = uriparse(alias)

            gCon.log(f"You {alias_uri} want to login!")

            # let's suppose that we want to login, first of all we create
            # an AliasApi and we pass the message
            self.wsctx.alias_api = AliasApi(alias_uri)
            msg = self.wsctx.alias_api.login(self.wsctx, password)


            # first of all I have to check the password, if it is correct
            # I send the OTP code.

            #answer = await send_msg_to_local_alias(self.wsctx, alias_uri,
            #                                       "hello world")

            #answer = "test ok"
            await self.websocket.send_text(f"remote answers {msg}")


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
                gCon.log("disconnect")


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
            await self.websocket.send_text(f"Error in request {err}")


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

