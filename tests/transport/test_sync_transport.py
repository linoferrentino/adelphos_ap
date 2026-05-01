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
from tests.transport.sync_mode.SyncTransport import SyncTransport
from app.logging import gCon

HOST_1 = "www.host1.org"
HOST_2 = "www.host2.org"


@pytest.fixture
def sync1():

    transport = SyncTransport()
    aroutable = TRoutable(transport)
    app = SyncApp(routes = aroutable.get_routes())
    return app


@pytest.fixture
def sync2():

    transport = SyncTransport()
    aroutable = TRoutable(transport)
    app = SyncApp(routes = aroutable.get_routes())
    return app


def test_sync_route(sync1):

    test = SyncTester(sync1)
    response = test.post("/inbox/lino", json = { 'msg' : 'do_all' })

    assert response.status_code == 200
    assert response.body == b'Hello lino! do_all'


def test_sync_transport(sync1):

    test = SyncTester(sync1)
    response = test.post("/post_msg_q", json = { 
                                                'dest' : HOST_2,
                                                'msg' : 'flag_99' })
    assert response.status_code == 202


