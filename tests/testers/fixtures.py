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



class SocialStub_DEP(SocialProvider):

    def __init__(self, user_list):
        self.users = { user: UserStub(user) for user in user_list }


    def local_user_exists(self, user: str) -> bool:
        user_local = self.users.get(user)
        if user_local is None:
            return False
        return True

    
    def _pri_get_user_stub(self, user):
        user_stub = self.users.get(user)
        if user_stub is None:
            raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST)
        return user_stub
 

    def incoming_message(self, user, message):
        user_stub = self._pri_get_user_stub(user)
        msg = message['msg']
        user_stub.new_msg(msg)


    async def outgoing_message(self, user, message):
        gCon.log(f"OOOO {user} {message} {self.transport}")
        await self.transport.post_json(user, {
            'msg' : message
            })


    def login_user(self, user):
        user_stub = self._pri_get_user_stub(user)
        return user_stub


    def create_or_register_user(self, user, *, listener = None):
        if user in self.users:
            raise AdelphosException(AdErrno.USER_ALREADY_EXISTING)
        self.users[user] = UserStub(user, listener)


class EchoKernel(Kernel):

    async def start_async(self, social):
        gCon.log(f"{id(self)} this is the social {social}")
        self.social = social

    
    async def stop_async(self):
        pass


    async def proc_msg(self, msg):
        host_dest = msg
        gCon.log(f"{id(self)} proc msg")
        gCon.log(f"I want to send message to {host_dest} social {self.social}")
        await self.social.outgoing_message(f"@EchoKernel@{host_dest}", "ping")
        return "DONE!"


class CliBypassStub(CliProvider):

    def __init__(self, kernel):
        super().__init__(kernel)


    async def accept(self, websocket):
        await websocket.accept()
        text = await websocket.receive_text()
        response = await self.kernel.proc_msg(text)
        await websocket.send_text(f"{response}")
        await websocket.close()



class CliHandlerStub(CliProvider):


    def __init__(self, kernel):
        super().__init__(kernel)


    async def accept(self, websocket):
        await websocket.accept()
        text = await websocket.receive_text()
        await websocket.send_text(f"Hello world, {text}!")
        await websocket.close()


        #client = ClientWs(self.kernel, websocket)
        #self.clients.append(client)
        #return client


#@pytest.fixture(scope = "module")
#def social_stub():
#    ss = SocialStub(('demo1', 'demo2'))
#    return ss
#
#
#@pytest.fixture(scope = "module")
#def cli_stub():
#    cli_stub = CliHandlerStub()
#    return cli_stub

