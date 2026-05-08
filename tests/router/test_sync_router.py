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
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester

import tests.test_constants as tc


@pytest.fixture
def app1(sync_gateway):
    routable = AdelphosRouter("test", None)
    app = SyncApp(tc.HOST_1, routable, sync_gateway)
    return app


def test_webfinger(app1):
    
    test1 = SyncTester(app1)
    url_query = f"{CNST.WEBFINGER_ROUTE}?val=wrong"
    response = test1.get(url_query)
    assert response.status_code == 401

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=malformed"
    response = test1.get(url_query)
    assert response.status_code == 404

    url_query = f"{CNST.WEBFINGER_ROUTE}?resource=acct:daemon@{tc.HOST_1}"
    response = test1.get(url_query)
    assert response.status_code == 404
