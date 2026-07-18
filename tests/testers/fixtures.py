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
import threading
import asyncio

from app.federation.SocialProvider import SocialProvider

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
#import copy
import yaml


def _build_routable_config_impl(instance_name, build_template, conf, mode):

    build_complete = build_template.format(**conf)
    kernel_conf = yaml.safe_load(build_complete)

    prefix = mode
    kernel = su.boot_kernel(f"{prefix}-{instance_name}", kernel_conf)
    aroutable = kernel.get_dep(Dependencies.ROUTER)

    if mode == 'sync':
        config = aroutable.conf
        host = config.get_host()
        app = SyncApp(host, aroutable, API_POINT)
        wrappedapp = SyncTester(app)
    else:
        app = StarletteWrap(routable = aroutable)
        wrappedapp = TestClient(app)

    return wrappedapp


@pytest.fixture(scope = "session", params = ['sync', 'async'])
def get_routable_app_param(request):

    def _build_routable_from_config(instance_name, build_template, conf):
        return _build_routable_config_impl(instance_name, build_template,
                                           conf, request.param)

    return _build_routable_from_config
 

@pytest.fixture(scope = "session")
def get_routable_app():

    def _build_routable_from_config(instance_name, build_structure, 
                                    conf, mode = "sync"):

        return _build_routable_config_impl(instance_name, build_structure,
                                           conf, mode)

    return _build_routable_from_config


@pytest.fixture(scope = "session")
def get_standalone_app():

    def _get_standalone_app(instance_name, build_template, conf):

        kernel_build_str = build_template.format(**conf)
        kernel_build = yaml.safe_load(kernel_build_str)

        server = ProcessWrapper()
        port = conf['_port_']
        return server.run_in_subprocess(su.boot_kernel, 
                                      (instance_name, kernel_build), 
                                      port)

    return _get_standalone_app


#@pytest.fixture(scope = "session")
@pytest.fixture
def aroutable(request):

    if hasattr(request, 'param'):
        conf = request.param
    else:
        conf = tconf.adelphos_toy_1_conf

    build_complete = tconf.testable_toy_kernel_template.format(**conf)
    kernel_conf = yaml.safe_load(build_complete)

    kernel = su.boot_new_kernel("test", kernel_conf)
    aroutable = kernel.get_dep(Dependencies.ROUTER)
    return aroutable 


#@pytest.fixture(scope = "session", params = ['sync', 'async'])
@pytest.fixture(params = ['sync', 'async'])
def app(aroutable, request):

    gCon.log(f"START FIXTURE APP {request.param}")

    try:
        loop = asyncio.get_running_loop()
        gCon.log(f"There is a loop! {id(loop)}")
    except RuntimeError:
        loop = get_loop()
        #loop = "NO loop"
        gCon.log(f"there was NO loop!, the external loop is {loop}")
        res = asyncio.set_event_loop(loop)
        #gCon.log(f"res {res}")
        #loop = asyncio.get_running_loop()
        #gCon.log(f"Now the async loop is {loop}")
 

    if request.param == 'sync':
        gCon.log("SYNC TEST")
        config = aroutable.conf
        host = config.get_host()
        app = SyncApp(host, aroutable, API_POINT)
        wrappedapp = SyncTester(app)
    else:
        gCon.log(f"ASYNC TEST in thread {threading.current_thread().native_id}")

        app = StarletteWrap(routable = aroutable)
        wrappedapp = TestClient(app)

    return wrappedapp


