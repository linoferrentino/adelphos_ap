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


from app.cli.CliProvider import CliProvider

from starlette.websockets import WebSocketDisconnect
from app.logging import gCon
from app.cli.CliParser import CliParser
from app.sdc.Dependencies import Dependencies
from app.exc.AdelphosException import AdelphosException
from app.api.UserSession import UserSession

import app.sdc.s_utils as sdc
import app.consts as CNST
import traceback
from app.core.sys.SysCallGateway import SysCallGateway

class StandardCliClient:

    def __init__(self, kernel, websocket):
        self.cli_api = kernel.get_dep(Dependencies.CLI_API)
        self.websocket = websocket
        self.session = UserSession(kernel)


    async def _internal_serve(self):

        while True:
            data = await self.websocket.receive_text()
            gCon.log(f"I have to process {data} on {self.cli_api}")
            #cp = CliParser(data)
            response = await self.cli_api.sys_call_gateway_msg(self.session, data)
            await self.websocket.send_text(response)


    async def serve_forever(self):
        self.running = True
        while True:
            try:
                await self.serve_a_cycle()
                continue
            except WebSocketDisconnect as wds:
                pass
            except Exception as ex:
                traceback.print_exc()
                await self.websocket.send_text(f"Server error {ex} we apologize.")
            break
        self.running = False


    async def serve_a_cycle(self):

        try:
            await self._internal_serve()
        except AdelphosException as err:
            await self.websocket.send_text(f"User Error: {err.out_str}")


class StandardCliProvider(CliProvider):

    def __init__(self, vhost):
        self.vhost = vhost
        self.clients = []


    async def serve_forever(self, websocket):

        await websocket.accept()
        client = StandardCliClient(self.vhost, websocket)
        self.clients.append(client)
        await client.serve_forever()



