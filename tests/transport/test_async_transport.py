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
import httpx
import time

from app.transport.async_mode.AsyncTransport import AsyncTransport
from tests.transport.TRoutable import TRoutable
from starlette.applications import Starlette
from starlette.testclient import TestClient
from tests.testers.ProcessWrapper import ProcessWrapper
from app.logging import gCon


@pytest.fixture
def app_t1():

    transport = AsyncTransport(None)
    aroutable = TRoutable(transport, "test")
    app = Starlette(routes = aroutable.get_routes())
    return app


@pytest.fixture
def remote_app():
    server = ProcessWrapper()
    with server.run_in_subprocess(TRoutable, 5999):
        yield


def test_async_route(app_t1):

    test = TestClient(app_t1) 
    
    response = test.post("/inbox/lino", json = { 'msg' : 'do_all' })

    assert response.status_code == 200
    assert response.content == b'Hello lino! do_all'


def test_remote_async(remote_app):

    response = httpx.post('http://127.0.0.1:5999/inbox/lino', json = {'msg' : 'do_all'})
    assert response.status_code == 200
    assert response.content == b'Hello lino! do_all'


