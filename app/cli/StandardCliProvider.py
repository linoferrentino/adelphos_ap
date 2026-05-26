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

class StandardCliClient:

    def __init__(self, kernel, websocket):
        self.kernel = kernel
        self.websocket = websocket
        self.session = UserSession()


    async def _internal_serve(self):

        while True:
            data = await self.websocket.receive_text()
            cp = CliParser(data)
            response = await self.kernel.proc_msg(cp, self.session)
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
            await self.websocket.send_text(f"Error: {err}")


# gateway
class StandardCliProvider(CliProvider):

    def __init__(self, vhost):
        self.vhost = vhost
        self.clients = []


    def _add_syscalls(self):
        self.syscalls = dict()
        kernel = self.vhost.get_dep(Dependencies.KERNEL)
        if kernel is None:
            raise Exception("No kernel to run.")

        syscalls = kernel.get_syscalls()
        for syscall in syscalls:
            self.syscalls[command_str] = (other_self, handler)


    async def serve_forever(self, websocket):

        await websocket.accept()
        kernel = self.vhost.get_dep(Dependencies.KERNEL)
        client = StandardCliClient(kernel, websocket)
        self.clients.append(client)
        await client.serve_forever()


    def start_sync(self):
        self._add_syscalls()


    def stop_sync(self):
        pass
