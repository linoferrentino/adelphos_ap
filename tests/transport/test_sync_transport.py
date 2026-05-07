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
#from tests.transport.TRoutable import HOST_1, HOST_2, FLAG_1, FLAG_2
import tests.test_constants as tc
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester
#from tests.testers.SyncGateway import SyncGateway
from tests.transport.sync_mode.SyncTransport import SyncTransport
#from tests.transport.sync_mode.loop import stop_loop, get_loop
from app.logging import gCon
from tests.testers.fixtures import sync_gateway
import json


#@pytest.fixture
#def sync_gateway():
#    get_loop()
#    gateway = SyncGateway()
#    yield gateway
#    stop_loop()


@pytest.fixture
def sync1(sync_gateway):

    aroutable = TRoutable(tc.FLAG_1)
    app = SyncApp(tc.HOST_1, aroutable, sync_gateway)
    return app


@pytest.fixture
def sync2(sync_gateway):

    aroutable = TRoutable(tc.FLAG_2)
    app = SyncApp(tc.HOST_2, aroutable, sync_gateway)
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
                                          'dest' : tc.HOST_2,
                                          'msg' : 'flag1' })
    assert response.status_code == 200
    jsonres = json.loads(response.body)
    assert jsonres['flag'] == 'hello'


def test_get_flag_no(sync1, sync2):

    test1 = SyncTester(sync1)
    test2 = SyncTester(sync2)

    with pytest.raises(Exception):
        response = test1.post("/get_remote_flag", json = { 
                                          'dest' : "www.nohost.com",
                                          'msg' : 'flag1' })

