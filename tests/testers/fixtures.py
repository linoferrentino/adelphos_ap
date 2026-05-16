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


class UserStub:

    def __init__(self, user, aListener = None):
        self.user = user
        if aListener is None:
            self.messages = []
            self.is_daemon = False
        else:
            self.listener = aListener
            self.is_daemon = True


    def new_msg(self, msg):
        if self.is_daemon:
            self.listener.new_post(msg)
        else:
            self.messages.append(msg)

    def count_msg(self):
        return len(self.messages)


    def pop_lst_msg(self):
        (self.messages, msg) = (self.messages[:-1], self.messages[-1])
        return msg


class SocialStub(SocialProvider):

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
        pass


    def login_user(self, user):
        user_stub = self._pri_get_user_stub(user)
        return user_stub


    def create_or_register_user(self, user, *, listener = None):
        if user in self.users:
            raise AdelphosException(AdErrno.USER_ALREADY_EXISTING)

        self.users[user] = UserStub(user, listener)


class EchoKernel(Kernel):

    async def start_async(self, social):
        pass

    
    async def stop_async(self):
        pass


    async def proc_msg(self, msg):
        pass



class CliHandlerStub(CliProvider):

    async def accept(self, websocket):
        await websocket.accept()
        text = await websocket.receive_text()
        await websocket.send_text(f"Hello world, {text}!")
        await websocket.close()


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

