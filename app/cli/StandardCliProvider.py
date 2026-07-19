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


import json

from app.cli.CliProvider import CliProvider

from starlette.websockets import WebSocketDisconnect
from app.logging import gCon
from app.cli.CliParser import CliParser
from app.sdc.Dependencies import Dependencies
from app.exc.AdelphosException import AdelphosException
from app.core.AdelphosCoreException import AdelphosCoreException
from app.api.UserSession import UserSession

import app.sdc.s_utils as sdc
import app.consts as CNST
import traceback
from app.core.sys.SysCallGateway import SysCallGateway
from app.core.ECoreErrno import ECoreErrno

from dataclasses import asdict
from app.cli.SysCall import SysCallAns


class StandardCliClient:

    def __init__(self, kernel, websocket):
        self.cli_api = kernel.get_dep(Dependencies.CLI_API)
        self.websocket = websocket
        self.session = UserSession(kernel)
        self.kernel = kernel


    async def _send_simple_success(self, response):
        await self._send_errno_str(ECoreErrno.DONE_OK, response)


    async def _send_errno_str(self, errno, response):
        if self.kernel.conf().is_human_output() == False:
            resobj = SysCallAns(errno, response)
            await self._send_output_ans_obj(resobj)
            return
        await self._out_final_str(response)


    async def _send_output_ans_obj(self, resojb):
        response_str = json.dumps(asdict(resojb))
        await self._out_final_str(response_str)


    async def _out_final_str(self, response_str):
        await self.websocket.send_text(response_str)


    async def _send_out_success(self, output):
        if isinstance(output, SysCallAns):
            await self._send_output_ans_obj(output)
        else:
            await self._send_simple_success(str(output))


    async def _internal_serve(self):

        while True:
            data = await self.websocket.receive_text()
            response = await self.cli_api.sys_call_gateway_msg(self.session, data)
            await self._send_out_success(response)


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
                await self._send_errno_str(ECoreErrno.ESYS, 
                                        f"Server error {ex} we apologize.")
            break
        self.running = False


    async def serve_a_cycle(self):

        try:
            await self._internal_serve()
        except AdelphosException as err:
            await self._send_errno_str(err.errno,
                                           f"User Error: {err.out_str}")
        except AdelphosCoreException as errcore:
            await self._send_errno_str(errcore.errno,
                                           f"Core Error: {errcore.out_str}")


class StandardCliProvider(CliProvider):

    def __init__(self, vhost):
        self.vhost = vhost
        self.clients = []


    async def serve_forever(self, websocket):

        await websocket.accept()
        client = StandardCliClient(self.vhost, websocket)
        self.clients.append(client)
        await client.serve_forever()



