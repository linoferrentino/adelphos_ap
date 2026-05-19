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


import pytest
import json

from app.federation.SocialProvider import SocialProvider
from app.federation.Kernel import Kernel

from tests.testers.SyncGateway import SyncGateway
from app.transport.bridge.loop import stop_loop, get_loop
from app.logging import gCon

from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno

from app.cli.CliProvider import CliProvider


class EchoKernel(Kernel):

    async def start_async(self):
        pass

    
    async def stop_async(self):
        pass


    async def proc_msg(self, msg):
        host_dest = msg
        gCon.log(f"I want to send message to {host_dest} social")
        #await self.social.outgoing_message(f"@EchoKernel@{host_dest}", "ping")
        return "DONE!"


class CliBypassStub(CliProvider):

    #def __init__(self, kernel):
    #    super().__init__(kernel)


    async def serve_forever(self, websocket):
        gCon.log("serve_forever ///////// STUB")
        await websocket.accept()
        text = await websocket.receive_text()
        response = await self.kernel.proc_msg(text)
        await websocket.send_text(f"{response}")
        await websocket.close()


class CliHandlerStub(CliProvider):

    #def __init__(self, kernel):
    #    super().__init__(kernel)


    async def serve_forever(self, websocket):
        gCon.log("serve_forever AAAAAA")
        await websocket.accept()
        text = await websocket.receive_text()
        await websocket.send_text(f"Hello world, {text}!")
        await websocket.close()




