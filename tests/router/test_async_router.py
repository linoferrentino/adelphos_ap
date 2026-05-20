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
from tests.testers.fixtures import CliHandlerStub
from tests.testers.fixtures import CliBypassStub
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
from app.federation.SimpleSocial import SimpleSocial
from app.cli.StandardCliProvider import StandardCliProvider

import tests.t_utils as tu
#import app.sdc.s_utils as sdc
#from app.sdc.Dependencies import Dependencies, get_dep
from app.sdc.Dependencies import Dependencies



@pytest.fixture(scope = "session")
def get_routable():

    def _build_routable_from_config(configuration, build_structure):

        social_stub = SimpleSocial(('demo1', 'demo2'))
        #kernel = EchoKernel()
        #cli_stub = StandardCliProvider(kernel)
        
        configuration['sdc'] = build_structure

        aroutable = AdelphosRouter("test", configuration)
                                    #, social = social_stub)
                                    #, kernel = kernel)
        #, cli_handler = cli_stub)
        return aroutable 

    return _build_routable_from_config





@pytest.fixture(scope = "module")
def aroutable(request):

    configuration = request.param if hasattr(request, 'param') \
            else tconf.adelphos_stub

    #social_stub = SimpleSocial(('demo1', 'demo2'))
    #kernel = EchoKernel()
    #cli_stub = CliHandlerStub(kernel)
    configuration['sdc'] = tconf.cli_stub_dep_conf

    aroutable = AdelphosRouter("test", configuration)
                                #, social = social_stub)
                                #, kernel = kernel)
                               #cli_handler = cli_stub)
    return aroutable 


@pytest.fixture(scope = "module", params = ['sync', 'async'])
def app(aroutable, request):

    if request.param == 'sync':
        config = aroutable.get_dep(Dependencies.CONFIG)
        host = config.get_host()
        app = SyncApp(host, aroutable)
        wrappedapp = SyncTester(app)
    else:
        app = StarletteWrap(routable = aroutable)
        wrappedapp = TestClient(app)

    return wrappedapp


#@pytest.fixture(scope = "session", params = ['sync', 'async'])
#def wrapped_app(get_routable):



@pytest.fixture(scope = "module", params = [ tconf.adelphos_stub, ])
def routable_stub(aroutable, request):
    return aroutable


@pytest.mark.parametrize('aroutable', ( tconf.adelphos_stub, ), indirect = True)
def test_context(app, aroutable):

    with app:
        app.post("", json = None)


def test_ws_1(app, aroutable):
    with app.websocket_connect(CNST.WS_ROUTE) as websocket:
        gCon.log("AAAAAA ws1")
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


#def test_ws_sync_async(get_routable):
#    pass


def test_post_from_kernel(get_routable):
    user_in = 'demo1'
    gCon.log("==================================== START TEST")
    routable1 = get_routable(tconf.adelphos_stub, tconf.simple_tester_config)
    routable2 = get_routable(tconf.adelphos_t2_test,
                             tconf.simple_tester_config)

    gCon.log(f"rout1 {routable1.sdc} rout2 {routable2.sdc}")

    #config = get_dep(Dependencies.CONFIG)
    config1 = routable1.get_dep(Dependencies.CONFIG)
    config2 = routable2.get_dep(Dependencies.CONFIG)

    host1 = config1.get_host()
    host2 = config2.get_host()
    gCon.log(f"host1 {host1} e {host2}")

    app1 = SyncApp(host1, routable1)
    app2 = SyncApp(host2, routable2)

    test1 = SyncTester(app1)
    test2 = SyncTester(app2)

    #host1 = tconf.adelphos_stub[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]
    #host2 = tconf.adelphos_t2_test[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]

    gCon.log(f"host1 {host1} host2 {host2}")

    with test1, test2:
        with test1.websocket_connect(CNST.WS_ROUTE) as websocket:
            websocket.send_text(f"sndpost @{user_in}@{host2} echo_test_x918")
            data = websocket.receive_text()
            gCon.log(f"++++++++ got data {data}")
            assert data == 'DONE!'
            websocket.close()
            
            #user_ob = routable2.get_social().login_user(user_in)
            #count_msg = user_ob.count_msg()
            #assert count_msg == 1

            #msg = user_ob.pop_lst_msg()
            #assert msg == 'echo_test_x918'



def test_post_inbox_ok(app, aroutable):
    user_in = 'demo1'
    url_post=CNST.USER_INBOX_ROUTE.format(username = user_in)
    jsonmsg = {
            'msg' : 'hello1 demo1 secret X8a9'
            }
    response = app.post(url_post, json = jsonmsg)
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
    #host = app.app.routable.config[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]
    host = config.get_host()

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=acct:demo1@{host}"
    response = test1.get(url_query)
    assert response.status_code == 200


