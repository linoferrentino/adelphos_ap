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

from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from app.AdelphosRouter import AdelphosRouter
from app.transport.async_mode.StarletteWrap import StarletteWrap

from tests.testers.fixtures import social_stub
import tests.test_constants as tc
import tests.adelphoi_test_config as tconf


@pytest.fixture
def app1(social_stub):
    aroutable = AdelphosRouter("test", tconf.adelphos_stub, social_stub)
    app = StarletteWrap(routable = aroutable)
    return app


def test_ws_1(app1):

    client = TestClient(app1) 
    with client.websocket_connect('/ws') as websocket:
        websocket.send_text("lino")
        data = websocket.receive_text()
        assert data == 'Hello, world! lino'


