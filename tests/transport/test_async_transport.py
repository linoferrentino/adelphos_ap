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

from app.transport.async_mode.AsyncTransport import AsyncTransport

from tests.transport.TRoutable import TRoutable

from starlette.applications import Starlette
from starlette.testclient import TestClient

@pytest.fixture
def app_t1():

    transport = AsyncTransport(None)
    aroutable = TRoutable(transport)
    app = Starlette(routes = aroutable.get_routes())
    return app


def test_async_route(app_t1):

    test = TestClient(app_t1) 
    
    response = test.post("/inbox/lino", json = { 'msg' : 'do_all' })

    assert response.status_code == 200
    assert response.content == b'Hello lino! do_all'



