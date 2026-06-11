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
import app.consts as CNST
from app.AdelphosRouter import AdelphosRouter
from app.sdc.Dependencies import Dependencies
import tests.adelphoi_test_config as tconf
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester
from app.logging import gCon
from app.transport.async_mode.StarletteWrap import StarletteWrap
from starlette.testclient import TestClient
from tests.testers.fixtures import get_routable_app

#@pytest.fixture(scope = "session", params = ['sync', 'async'])
#def get_routable_app(request):
#
#    def _build_routable_from_config(configuration, build_structure):
#
#        configuration['sdc'] = build_structure
#
#        aroutable = AdelphosRouter("test", configuration)
#
#        if request.param == 'sync':
#            config = aroutable.get_dep(Dependencies.CONFIG)
#            host = config.get_host()
#            app = SyncApp(host, aroutable)
#            wrappedapp = SyncTester(app)
#        else:
#            app = StarletteWrap(routable = aroutable)
#            wrappedapp = TestClient(app)
#
#        with wrappedapp as app1:
#            return app1
#
#    return _build_routable_from_config
#


def test_simple_router(get_routable_app):

    app = get_routable_app('test1', tconf.adelphos_stub, tconf.simple_tester_config)
    with app.websocket_connect(CNST.WS_ROUTE) as websocket:
        websocket.send_text("dbg.echo msg lino99")
        data = websocket.receive_text()
        assert data == 'hello lino99!'


