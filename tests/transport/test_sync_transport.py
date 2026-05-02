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

from tests.transport.TRoutable import TRoutable
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester
from tests.testers.SyncGateway import SyncGateway
from tests.transport.sync_mode.SyncTransport import SyncTransport
from app.logging import gCon

HOST_1 = "www.host1.org"
HOST_2 = "www.host2.org"

FLAG_1 = "XXXzzz"
FLAG_1_NEW = "XXXZZZ"

FLAG_2 = "XXXyyy"
FLAG_2_NEW = "XXXYYY"


@pytest.fixture
def sync_gateway():
    gateway = SyncGateway()
    return gateway


@pytest.fixture
def sync1(sync_gateway):

    transport = SyncTransport(HOST_1, sync_gateway)
    aroutable = TRoutable(transport, FLAG_1)
    app = SyncApp(routes = aroutable.get_routes())
    return app


@pytest.fixture
def sync2(sync_gateway):

    transport = SyncTransport(HOST_2, sync_gateway)
    aroutable = TRoutable(transport, FLAG_2)
    app = SyncApp(routes = aroutable.get_routes())
    return app


def test_sync_route(sync1):

    test = SyncTester(sync1)
    response = test.post("/inbox/lino", json = { 'msg' : 'do_all' })

    assert response.status_code == 200
    assert response.body == b'Hello lino! do_all'


def test_get_flag(sync1, sync2):

    test1 = SyncTester(sync1)
    test2 = SyncTester(sync2)
    response = test1.post("/get_remote_flag", json = { 
                                          'dest' : HOST_2,
                                          'msg' : 'flag1' })
    assert response.status_code == 202


