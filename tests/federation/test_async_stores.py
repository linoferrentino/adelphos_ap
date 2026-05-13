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

#from tests.federation.schema_simple import LOCALHOST, LOCALHOST1, OTHERHOST
#from tests.federation.schema_simple import TYPE_T1, TYPE_T2
#from tests.federation.schema_simple import FederatedUriTest
#from tests.federation.schema_simple import my_test_schema_init
#
#
#from app.AdelphosAsyncGateway import AdelphosAsyncGateway
#from app.AdelphosAsyncGateway import ad_get_app
#
#from app.store.MemoryStore import MemoryStore
#
#from starlette.responses import HTMLResponse
#from starlette.testclient import TestClient
#
#
#async def app(scope, receive, send):
#    assert scope['type'] == 'http'
#    response = HTMLResponse('<html><body>Hello, world!</body></html>')
#    await response(scope, receive, send)
#
#
#@pytest.fixture
#def ad1():
#
#    ad1 = TestClient(ad_get_app('www.ex.com'))
#    return ad1


#def test_async_comm(ad1):
def test_async_comm():
    assert False
    response = ad1.get('/')
    assert response.status_code == 200

