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
import yaml


from app.cli.CliProvider import CliProvider
from app.consts import ROOT_PATH_DEFAULT
from app.exc.AdelphosException import AdErrno
from app.exc.AdelphosException import AdelphosException
from app.federation.SocialProvider import SocialProvider
from app.logging import gCon
from app.sdc.Dependencies import Dependencies
from app.transport.async_mode.StarletteWrap import StarletteWrap
from app.transport.bridge.loop import stop_loop, get_loop
from starlette.testclient import TestClient
from tests.testers.ProcessWrapper import ProcessWrapper
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncGateway import SyncGateway
from tests.testers.SyncTester import SyncTester
import app.consts as CNST
import app.sdc.s_utils as su
import tests.adelphoi_test_config as tconf

from tests.testers.SimulFediverse import SimulFediverse


def _build_routable_config_impl(instance_name, build_template, conf, mode):

    build_complete = build_template.format(**conf)
    kernel_conf = yaml.safe_load(build_complete)

    gCon.log(f"This is the build")
    gCon.log(kernel_conf)

    prefix = mode
    kernel = su.boot_kernel(f"{prefix}-{instance_name}", kernel_conf)
    aroutable = kernel.get_dep(Dependencies.ROUTER)

    if mode == 'sync':
        config = aroutable.conf
        host = config.get_host()
        app = SyncApp(host, aroutable, ROOT_PATH_DEFAULT)
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


def _build_simul_fediverse(fediverse_template, conf):
    if conf is not None:
        federated_world = federated_world_template.format(**conf)
    else:
        federated_world = federated_world_template

    fed_world = yaml.safe_load(federated_world)
    gCon.log(f"I have to build this world {fed_world}")
    world = FederatedWorld(federated_world)
    return world


@pytest.fixture(scope = "session")
def simulated_fediverse():
    def _build_simul_fediverse(fediverse_template, conf = None):
        sim_fed = SimulFediverse(fediverse_template, conf)
        return sim_fed
    #return _build_simul_fediverse_impl(fediverse_template, conf)

    return _build_simul_fediverse


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


@pytest.fixture(params = ['sync', 'async'])
def app(aroutable, request):

    if request.param == 'sync':
        config = aroutable.conf
        host = config.get_host()
        app = SyncApp(host, aroutable, ROOT_PATH_DEFAULT)
        wrappedapp = SyncTester(app)
    else:
        app = StarletteWrap(routable = aroutable, root_path = ROOT_PATH_DEFAULT)
        wrappedapp = TestClient(app)

    return wrappedapp


