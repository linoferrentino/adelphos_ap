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


import pytest

from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from app.AdelphosRouter import AdelphosRouter
from app.transport.async_mode.StarletteWrap import StarletteWrap

from tests.testers.fixtures import CliBypassStub
import tests.test_constants as tc
import tests.adelphoi_test_config as tconf
from app.transport.bridge.loop import stop_loop, get_loop
from tests.testers.SyncApp import SyncApp
import app.consts as CNST
from tests.testers.SyncTester import SyncTester
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import parse_exc_str
from app.exc.AdelphosException import AdErrno
from app.logging import gCon
from app.federation.SimpleSocial import SimpleSocial

import tests.t_utils as tu
from app.sdc.Dependencies import Dependencies
from tests.testers.fixtures import get_routable_app
from tests.testers.fixtures import app, aroutable
import tests.social.social_tests as stests


@pytest.mark.parametrize('aroutable', ( tconf.adelphos_stub, ), indirect = True)
def test_context(app, aroutable):

    app.post("", json = None)


def test_ws_1(app):
    with app.websocket_connect(CNST.WS_ROUTE) as websocket:
        websocket.send_text("lino")
        data = websocket.receive_text()
        assert data == 'Hello world, lino!'


def test_post_inbox_KO(app, aroutable):
    user_in = 'demo_WHAT'
    url_post=CNST.USER_INBOX_ROUTE.format(username = user_in)
    url_post=CNST.API_POINT + url_post
    jsonmsg = {
            'msg' : f'hello1 {user_in} secret X8a9',
            'actor' : 'demo2',
            }
    response = app.post(url_post, json = jsonmsg)
    tu.assert_error_code_in_response(response, AdErrno.EINVALID_SIGNATURE)

    user_in = 'demo1'
    url_post=CNST.USER_INBOX_ROUTE.format(username = user_in)
    url_post=CNST.API_POINT + url_post
    jsonmsg = {
            'msg' : f'hello1 {user_in} secret X8a9',
            'actor' : 'demo99',
            }
    response = app.post(url_post, json = jsonmsg)
    assert response.status_code == 401


def test_post_from_kernel(get_routable_app):
    test1 = get_routable_app('test1', tconf.adelphos_stub, 
                                 tconf.simple_tester_config)
    test2 = get_routable_app('test2', tconf.adelphos_t2_test,
                             tconf.simple_tester_config)

    host2 = tconf.adelphos_t2_test['General']['host']
    stests._test_sndpost_to_host(test1, test2, host2, 'demo1', 'demo77')


def OLD_test_post_from_kernel(get_routable_app):
    user_in = 'demo1'
    test1= get_routable_app('test1', tconf.adelphos_stub, 
                                 tconf.simple_tester_config)
    test2 = get_routable_app('test2', tconf.adelphos_t2_test,
                             tconf.simple_tester_config)

    host2 = tconf.adelphos_t2_test['General']['host']


    with test1, test2:
        with test1.websocket_connect(CNST.WS_ROUTE) as websocket:
            websocket.send_text(
    f"dbg.sndpost to @{user_in}@{host2} msg echo_test_x918 from demo1")
            data = websocket.receive_text()
            assert parse_exc_str(data) == AdErrno.USER_DOES_NOT_EXIST

            user_in = 'demo77'

            websocket.send_text(
    f"dbg.sndpost to @{user_in}@{host2} msg echo_test_x918 from demo1")
            data = websocket.receive_text()
            assert data == "DONE!"

            websocket.close()
            
            user_ob = test2.app.routable.get_dep(
                    Dependencies.SOCIAL).login_user(user_in)
            count_msg = user_ob.count_msg()
            assert count_msg == 1

            msg = user_ob.pop_lst_msg()
            assert msg == 'echo_test_x918'


def test_post_inbox_ok(app, aroutable):
    user_in = 'demo1'
    url_post=CNST.USER_INBOX_ROUTE.format(username = user_in)
    url_post=CNST.API_POINT + url_post
    jsonmsg = {
            'msg' : '@demo1 hello1 demo1 secret X8a9',
            'actor' : 'demo2'
            }
    headers = {
            'x-simple-signature' : "BACKDOOR_GO"
            }
    response = app.post(url_post, json = jsonmsg, headers = headers)
    assert response.status_code == 202

    social = aroutable.get_dep(Dependencies.SOCIAL)
    user_ob = social.login_user(user_in)

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

    config = aroutable.get_dep(Dependencies.CONFIG)
    host = config.get_host()

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=acct:demo1@{host}"
    response = test1.get(url_query)
    assert response.status_code == 200


