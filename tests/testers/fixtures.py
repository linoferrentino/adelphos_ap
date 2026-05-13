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

from tests.testers.SyncGateway import SyncGateway
from tests.transport.sync_mode.loop import stop_loop, get_loop
from app.logging import gCon

from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno


class UserStub:

    def __init__(self, user):
        self.user = user
        self.messages = []


    def new_msg(self, msg):
        self.messages.append(msg)


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
 

    def post_message(self, user, message):
        user_stub = self._pri_get_user_stub(user)
        msg = message['msg']
        user_stub.new_msg(msg)


    def login_user(self, user):
        user_stub = self._pri_get_user_stub(user)
        return user_stub


#@pytest.fixture(scope = "module")
#def sync_gateway():
#    get_loop()
#    gateway = SyncGateway()
#    yield gateway
#    stop_loop()


@pytest.fixture(scope = "module")
def social_stub():
    ss = SocialStub(('demo1', 'demo2'))
    return ss


