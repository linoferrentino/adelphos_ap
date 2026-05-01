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
from app.logging import gCon


@pytest.fixture
def sync1():
    aroutable = TRoutable()
    app = SyncApp(routes = aroutable.get_routes())
    return app


def test_sync_route(sync1):

    test = SyncTester(sync1)

    response = test.post("/inbox/lino", json = { 'msg' : 'do_all' })

    assert response.status_code == 200
    assert response.body == b'Hello lino! do_all'

