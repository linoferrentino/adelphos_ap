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

import app.sdc.s_utils as sdc
import app.consts as CNST

class StandardCliClient:

    def __init__(self, kernel, websocket):
        self.kernel = kernel
        self.websocket = websocket
        gCon.log(f"cli api ")
        self.cli_api = sdc.get_ob(CNST.CLI_API)


    async def _internal_serve(self):

        while True:
            data = await self.websocket.receive_text()
            #gCon.log(f">>>>>>>>> {data}")
            #cli_parser = CliParser(data)
            response = await self.kernel.proc_msg(data)
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
                await self.websocket.send_text(f"Server error, we apologize.")

            break
        self.running = False


    async def serve_a_cycle(self):

        try:

            await self._internal_serve()

        except AdelphosException as err:

            # this is a "benign" error, we eat the exception and continue
            await self.websocket.send_text(f"Error: {err}")


class StandardCliProvider(CliProvider):

    def __init__(self, kernel):
        self.kernel = kernel
        self.clients = []


    async def serve_forever(self, websocket):

        await websocket.accept()
        client = StandardCliClient(self.kernel, websocket)
        self.clients.append(client)
        await client.serve_forever()


