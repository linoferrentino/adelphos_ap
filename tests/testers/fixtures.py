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

from app.federation.SocialProvider import SocialProvider

from tests.testers.SyncGateway import SyncGateway
from tests.transport.sync_mode.loop import stop_loop, get_loop
from app.logging import gCon


class UserStub:

    def __init__(self, user):
        self.user = user


class SocialStub(SocialProvider):


    def __init__(self, user_list):

        self.users = { user: UserStub(user) for user in user_list }


    def get_user_handle(self, user: str) -> int:
        pass


    def local_user_exists(self, user: str) -> bool:
        user_local = self.users.get(user)
        if user_local is None:
            return False
        return True


    def post_message(self, user_handle, message):
        pass



@pytest.fixture
def sync_gateway():
    get_loop()
    gateway = SyncGateway()
    yield gateway
    stop_loop()


@pytest.fixture
def social_stub():
    ss = SocialStub(('demo1', 'demo2'))
    return ss


