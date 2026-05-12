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
from tests.testers.fixtures import sync_gateway
from tests.testers.SyncApp import SyncApp
import app.consts as CNST
from tests.testers.SyncTester import SyncTester
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno


#@pytest.fixture
#def app1_async(social_stub):
#    aroutable = AdelphosRouter("test", tconf.adelphos_stub, social_stub)
#    app = StarletteWrap(routable = aroutable)
#    return app


@pytest.fixture(scope = "module", params = ['sync', 'async'])
def app1(social_stub, sync_gateway, request):
    aroutable = AdelphosRouter("test", tconf.adelphos_stub, social_stub)
    if request.param == 'sync':
        host = aroutable.config[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]
        app = SyncApp(host, aroutable, sync_gateway)
        wrappedapp = SyncTester(app)
    else:
        app = StarletteWrap(routable = aroutable)
        wrappedapp = TestClient(app)
    return wrappedapp


def test_ws_1(app1):

    #client = TestClient(app1) 
    with app1.websocket_connect(CNST.WS_ROUTE) as websocket:
        websocket.send_text("lino")
        data = websocket.receive_text()
        assert data == 'Hello, world! lino'


def test_post_inbox_KO(app1, social_stub):
    user_in = 'demo_WHAT'
    url_post=CNST.USER_INBOX_ROUTE.format(username = user_in)
    jsonmsg = {
            'msg' : f'hello1 {user_in} secret X8a9'
            }
    with pytest.raises(AdelphosException):
        response = app1.post(url_post, json = jsonmsg)


def test_post_inbox_ok(app1, social_stub):
    url_post=CNST.USER_INBOX_ROUTE.format(username = 'demo1')
    jsonmsg = {
            'msg' : 'hello1 demo1 secret X8a9'
            }
    response = app1.post(url_post, json = jsonmsg)
    assert response.status_code == 202


def test_webfinger(app1):
    
    test1 = app1
    url_query = f"{CNST.WEBFINGER_ROUTE}?val=wrong"
    response = test1.get(url_query)
    assert response.status_code == 401

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=malformed"
    response = test1.get(url_query)
    assert response.status_code == 401

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=acct:daemon@{tc.HOST_1}"
    response = test1.get(url_query)
    assert response.status_code == 404

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=acct:demo1@www.external.it"
    response = test1.get(url_query)
    assert response.status_code == 404

    host = app1.app.routable.config[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=acct:demo1@{host}"
    response = test1.get(url_query)
    assert response.status_code == 200


