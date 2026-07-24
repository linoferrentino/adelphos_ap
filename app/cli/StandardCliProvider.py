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
from app.exc.AdelphosException import AdErrno
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
        self.cli_presenter = kernel.get_dep(Dependencies.CLI_PRESENTER)
        self.websocket = websocket
        self.session = UserSession(self)
        self.kernel = kernel
        self.sessions = dict()
        self.save_session = None


    def push_session(self, alias):
        if self.save_session is not None:
            raise AdelphosException(AdErrno.ESESSION_ALREADY_PUSHED)

        alias_session = self.sessions.get(alias)
        if alias_session is None:
            alias_session = UserSession(self)
            self.sessions[alias] = alias_session

        self.save_session = self.session
        self.session = alias_session
        return alias_session


    async def _out_final_str(self, response_str):
        await self.websocket.send_text(response_str)


    async def _internal_serve(self):

        while True:
            data = await self.websocket.receive_text()
            response = await self.cli_api.sys_call_gateway_msg(self.session, data)
            response_str = self.cli_presenter.present_to_user_ok(response)
            await self._out_final_str(response_str)


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
                await self._process_exception(ex)
            break
        self.running = False


    async def serve_a_cycle(self):

        try:
            await self._internal_serve()
        except AdelphosException as err:
            await self._process_exception(err)
        except AdelphosCoreException as errcore:
            await self._process_exception(errcore)


    async def _process_exception(self, exc):
        response_str = self.cli_presenter.present_to_user_exc(exc)
        await self._out_final_str(response_str)


class StandardCliProvider(CliProvider):

    def __init__(self, vhost):
        self.vhost = vhost
        self.clients = []


    async def serve_forever(self, websocket):

        await websocket.accept()
        client = StandardCliClient(self.vhost, websocket)
        self.clients.append(client)
        await client.serve_forever()



