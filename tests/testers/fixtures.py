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

#from app.AdelphosRouter import AdelphosRouter
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester
from tests.testers.ProcessWrapper import ProcessWrapper
import tests.adelphoi_test_config as tconf
import app.consts as CNST
from app.transport.async_mode.StarletteWrap import StarletteWrap
from starlette.testclient import TestClient
from app.consts import API_POINT
import app.sdc.s_utils as su


def _build_routable_config_impl(instance_name, configuration,
                                build_structure, mode):

    configuration['sdc'] = build_structure

    prefix = mode
    #aroutable = AdelphosRouter(f"{prefix}-{instance_name}", configuration)
    kernel = su.build_kernel(f"{prefix}-{instance_name}", configuration)
    aroutable = kernel.get_dep(Dependencies.ROUTER)

    if mode == 'sync':
        gCon.log("====================== SYNC")
        config = aroutable.conf()
        host = config.get_host()
        app = SyncApp(host, aroutable, API_POINT)
        wrappedapp = SyncTester(app)
    else:
        gCon.log("====================== ASYNC")
        app = StarletteWrap(routable = aroutable)
        wrappedapp = TestClient(app)

    return wrappedapp


@pytest.fixture(scope = "session", params = ['sync', 'async'])
def get_routable_app_param(request):

    def _build_routable_from_config(instance_name, configuration, 
                                    build_structure):
        return _build_routable_config_impl(instance_name, configuration,
                                           build_structure, request.param)

    return _build_routable_from_config
 

@pytest.fixture(scope = "session")
def get_routable_app():

    def _build_routable_from_config(instance_name, configuration, 
                                    build_structure, mode = "sync"):
        return _build_routable_config_impl(instance_name, configuration,
                                           build_structure, mode)


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


@pytest.fixture(scope = "session")
def aroutable(request):

    configuration = request.param if hasattr(request, 'param') \
            else tconf.routable_test_kernel
    gCon.log(f"conf {configuration}")
    configuration['sdc'] = tconf.cli_stub_dep_conf
    aroutable = AdelphosRouter("test", configuration)
    return aroutable 


@pytest.fixture(scope = "session", params = ['sync', 'async'])
def app(aroutable, request):

    if request.param == 'sync':
        config = aroutable.conf()
        host = config.get_host()
        app = SyncApp(host, aroutable, API_POINT)
        wrappedapp = SyncTester(app)
    else:
        app = StarletteWrap(routable = aroutable)
        wrappedapp = TestClient(app)

    return wrappedapp


#class CliBypassStub(CliProvider):
#
#    async def serve_forever(self, websocket):
#        await websocket.accept()
#        text = await websocket.receive_text()
#        response = await self.kernel.proc_msg(text)
#        await websocket.send_text(f"{response}")
#        await websocket.close()



