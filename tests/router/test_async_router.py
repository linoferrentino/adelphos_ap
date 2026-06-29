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

#from app.AdelphosRouter import AdelphosRouter
from app.transport.async_mode.StarletteWrap import StarletteWrap

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
import tests.daemon.daemon_tests as dtests


@pytest.mark.parametrize('aroutable', ( tconf.simple_toy_conf, ),
                         indirect = True)
def test_context(app, aroutable):

    app.post("", json = None)


def test_ws_1(app):
    with app.websocket_connect(CNST.WS_ROUTE) as websocket:
        websocket.send_text("lino")
        data = websocket.receive_text()
        assert data == 'Hello world, lino!'


def test_post_inbox_KO(app, aroutable):
    with app:
        user_in = 'demo_WHAT'
        url_post=CNST.USER_INBOX_ROUTE.format(username = user_in)
        url_post=CNST.API_POINT + url_post
        jsonmsg = {
                'msg' : f'hello1 {user_in} secret X8a9',
                'actor' : 't1',
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
    test1 = get_routable_app('test1', tconf.routable_test_kernel, 
                                 tconf.simple_tester_config)
    test2 = get_routable_app('test2', tconf.routable_test2_kernel,
                             tconf.simple_tester_config)

    host2 = tconf.routable_test2_kernel['General']['host']
    stests._test_sndpost_to_host(test1, test2, host2, 'x1', 't99', 't1')


def test_remote_add(get_routable_app):
    test1 = get_routable_app('test1', tconf.routable_test_kernel, 
                                 tconf.simple_tester_config)
    test2 = get_routable_app('test2', tconf.routable_test2_kernel,
                             tconf.simple_tester_config)

    host2 = tconf.routable_test2_kernel['General']['host']
    dtests._test_remote_add(test1, test2, host2)


def test_post_inbox_ok(app, aroutable):
    user_in = 't1'
    url_post=CNST.USER_INBOX_ROUTE.format(username = user_in)
    url_post=CNST.API_POINT + url_post
    jsonmsg = {
            'msg' : '@t1 hello1 demo1 secret X8a9',
            'actor' : 't2'
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

    config = aroutable.conf()
    host = config.get_host()

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=acct:t1@{host}"
    response = test1.get(url_query)
    assert response.status_code == 200


