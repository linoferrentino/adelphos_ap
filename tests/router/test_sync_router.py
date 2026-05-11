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


import app.consts as CNST
from app.AdelphosRouter import AdelphosRouter

from tests.testers.fixtures import sync_gateway
from tests.testers.fixtures import social_stub

from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester

import tests.test_constants as tc
import tests.adelphoi_test_config as tconf



@pytest.fixture
def app1(sync_gateway, social_stub):
    routable = AdelphosRouter("test", tconf.adelphos_stub, social_stub)
    host = routable.config[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]
    app = SyncApp(host, routable, sync_gateway)
    return app


def test_ws_sync(app1):

    test1 = SyncTester(app1)
    with test1.websocket_connect('/ws') as websocket:
        websocket.send_text("lino")
        data = websocket.receive_text()
        assert data == 'Hello, world! lino'


def test_webfinger(app1):
    
    test1 = SyncTester(app1)
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

    host = app1.routable.config[CNST.CNF_GENERAL_SECTION][CNST.CNF_HOST_KEY]

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=acct:demo1@{host}"
    response = test1.get(url_query)
    assert response.status_code == 200


