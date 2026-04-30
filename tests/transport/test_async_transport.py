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

from app.transport.async_mode.AsyncTransport import AsyncTransport

from tests.transport.TRoutable import TRoutable

from starlette.applications import Starlette
from starlette.testclient import TestClient



def test_async_route():

    aroutable = TRoutable()

    app = Starlette(routes = aroutable.get_routes())

    test = TestClient(app) 

    response = test.post("/inbox/lino", json = { 'msg' : 'do_all' })

    assert response.status_code == 200
    assert response.content == b'Hello lino! do_all'
