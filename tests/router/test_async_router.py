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

#from tests.testers.fixtures import social_stub, cli_stub
from tests.testers.fixtures import SocialStub
from tests.testers.fixtures import CliHandlerStub
from tests.testers.fixtures import EchoKernel
import tests.test_constants as tc
import tests.adelphoi_test_config as tconf
#from tests.testers.fixtures import sync_gateway
from app.transport.bridge.loop import stop_loop, get_loop
from tests.testers.SyncApp import SyncApp
import app.consts as CNST
from tests.testers.SyncTester import SyncTester
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import parse_exc
from app.exc.AdelphosException import AdErrno
from app.logging import gCon

import tests.t_utils as tu


@pytest.fixture(scope = "module")
def aroutable(request):

    configuration = request.param if hasattr(request, 'param') \
            else tconf.adelphos_stub

    social_stub = SocialStub(('demo1', 'demo2'))
    kernel = EchoKernel()
    cli_stub = CliHandlerStub(kernel)

    aroutable = AdelphosRouter("test", configuration, 
                               social_stub, kernel = kernel,
                               cli_handler = cli_stub)
    return aroutable 


@pytest.fixture(scope = "module", params = ['sync', 'async'])
def app(aroutable, request):

    if request.param == 'sync':
        host = aroutable.config[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]
        app = SyncApp(host, aroutable)
        wrappedapp = SyncTester(app)
    else:
        app = StarletteWrap(routable = aroutable)
        wrappedapp = TestClient(app)

    return wrappedapp


@pytest.fixture(scope = "module", params = [ tconf.adelphos_stub, ])
def routable_stub(aroutable, request):
    return aroutable


@pytest.mark.parametrize('aroutable', ( tconf.adelphos_stub, ), indirect = True)
def test_context(app, aroutable):

    with app:
        app.post("", json = None)


def test_ws_1(app, aroutable):
    with app.websocket_connect(CNST.WS_ROUTE) as websocket:
        websocket.send_text("lino")
        data = websocket.receive_text()
        assert data == 'Hello world, lino!'


def test_post_inbox_KO(app, aroutable):
    user_in = 'demo_WHAT'
    url_post=CNST.USER_INBOX_ROUTE.format(username = user_in)
    jsonmsg = {
            'msg' : f'hello1 {user_in} secret X8a9'
            }
    response = app.post(url_post, json = jsonmsg)
    tu.assert_error_code_in_response(response, AdErrno.USER_DOES_NOT_EXIST)


def test_post_from_kernel():
    pass


def test_post_inbox_ok(app, aroutable):
    user_in = 'demo1'
    url_post=CNST.USER_INBOX_ROUTE.format(username = user_in)
    jsonmsg = {
            'msg' : 'hello1 demo1 secret X8a9'
            }
    response = app.post(url_post, json = jsonmsg)
    assert response.status_code == 202

    user_ob = aroutable.get_social().login_user(user_in)

    count_msg = user_ob.count_msg()
    assert count_msg == 1

    msg = user_ob.pop_lst_msg()
    assert msg == 'hello1 demo1 secret X8a9'

    count_msg = user_ob.count_msg()
    assert count_msg == 0


def test_webfinger(app, aroutable):
    test1 = app
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

    host = app.app.routable.config[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=acct:demo1@{host}"
    response = test1.get(url_query)
    assert response.status_code == 200


