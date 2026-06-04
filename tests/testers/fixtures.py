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
import json

from app.federation.SocialProvider import SocialProvider
from app.federation.Kernel import Kernel

from tests.testers.SyncGateway import SyncGateway
from app.transport.bridge.loop import stop_loop, get_loop
from app.logging import gCon

from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno

from app.cli.CliProvider import CliProvider
from app.sdc.Dependencies import Dependencies

from app.AdelphosRouter import AdelphosRouter
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester
from tests.testers.ProcessWrapper import ProcessWrapper
import tests.adelphoi_test_config as tconf
import app.consts as CNST
from app.transport.async_mode.StarletteWrap import StarletteWrap
from starlette.testclient import TestClient


@pytest.fixture(scope = "session")
def get_routable_app():

    def _build_routable_from_config(instance_name, configuration, 
                                    build_structure, mode = 'sync'):
        configuration['sdc'] = build_structure
        aroutable = AdelphosRouter(instance_name, configuration)

        if mode == 'sync':
            config = aroutable.get_dep(Dependencies.CONFIG)
            host = config.get_host()
            app = SyncApp(host, aroutable)
            wrappedapp = SyncTester(app)
        else:
            app = StarletteWrap(routable = aroutable)
            wrappedapp = TestClient(app)

        with wrappedapp:
            return wrappedapp

    return _build_routable_from_config


@pytest.fixture(scope = "session")
def get_standalone_app():

    def _get_standalone_app(instance_name, configuration, build_structure):

        configuration['sdc'] = build_structure
        server = ProcessWrapper()
        port = configuration['General']['port']
        return server.run_in_subprocess(AdelphosRouter, 
                                      (instance_name, configuration), 
                                      port)

    return _get_standalone_app

#def get_standalone_app():
#
#    def _get_standalone_app(instance_name, configuration, build_structure):
#
#        configuration['sdc'] = build_structure
#        server = ProcessWrapper()
#        port = configuration['General']['port']
#
#        ad1 = server.run_in_subprocess(AdelphosRouter, 
#                                      (instance_name, configuration), 
#                                      port)
#        gCon.log(f"run_is {ad1}")
#        with ad1:
#            return ad1
#            
#
#    return _get_standalone_app



@pytest.fixture(scope = "session")
def aroutable(request):

    configuration = request.param if hasattr(request, 'param') \
            else tconf.adelphos_stub
    configuration['sdc'] = tconf.cli_stub_dep_conf
    aroutable = AdelphosRouter("test", configuration)
    return aroutable 


@pytest.fixture(scope = "session", params = ['sync', 'async'])
def app(aroutable, request):

    if request.param == 'sync':
        config = aroutable.get_dep(Dependencies.CONFIG)
        host = config.get_host()
        app = SyncApp(host, aroutable)
        wrappedapp = SyncTester(app)
    else:
        app = StarletteWrap(routable = aroutable)
        wrappedapp = TestClient(app)

    with wrappedapp:
        yield wrappedapp


class CliBypassStub(CliProvider):

    async def serve_forever(self, websocket):
        await websocket.accept()
        text = await websocket.receive_text()
        response = await self.kernel.proc_msg(text)
        await websocket.send_text(f"{response}")
        await websocket.close()



