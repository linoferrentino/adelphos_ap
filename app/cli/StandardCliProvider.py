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
import app.sdc.s_utils as sdc
import app.consts as CNST
import traceback

class StandardCliClient:

    def __init__(self, kernel, websocket):
        self.kernel = kernel
        self.websocket = websocket
        #self.cli_api = sdc.get_dep(CNST.CLI_API)
        gCon.log(f"HELLO kernel {self.kernel} webs {self.websocket}")


    async def _internal_serve(self):

        while True:
            gCon.log(f"{self.websocket} here I internal serve")
            data = await self.websocket.receive_text()
            gCon.log(f">>>>>>>>>got: {data} <<<<<<<<<<<<<<<<<<<<<< {self.kernel}")
            response = await self.kernel.proc_msg(data)
            #self.websocket.send_text(response)
            await self.websocket.send_text(response)
            #await self.websocket.sending_text_async(response)


    async def serve_forever(self):
        self.running = True
        while True:
            try:

                await self.serve_a_cycle()
                continue

            except WebSocketDisconnect as wds:
                pass

            except Exception as ex:
                await self.websocket.send_text(f"Server error, we apologize.")

            break
        self.running = False


    async def serve_a_cycle(self):
        gCon.log("serve_a_cycle")

        try:

            await self._internal_serve()

        except AdelphosException as err:

            # this is a "benign" error, we eat the exception and continue
            await self.websocket.send_text(f"Error: {err}")
        #except WebSocketDisconnect as wds:
        #        pass

        #except Exception as ex:
        #    gCon.log("trace?")
        #    traceback.print_exc()
        #    raise


class StandardCliProvider(CliProvider):

    def __init__(self, vhost):
        self.vhost = vhost
        self.clients = []


    async def serve_forever(self, websocket):

        await websocket.accept()
        kernel = self.vhost.get_dep(Dependencies.KERNEL)
        gCon.log(f"StandardCliProvider ================ serve! {self.vhost} kern {kernel}")
        client = StandardCliClient(kernel, websocket)
        self.clients.append(client)
        await client.serve_forever()


