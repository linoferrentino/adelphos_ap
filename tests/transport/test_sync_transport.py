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
import yaml
import json

from tests.transport.TRoutable import TRoutable
import tests.test_constants as tc
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester
from tests.transport.sync_mode.SyncTransport import SyncTransport
from app.transport.bridge.loop import stop_loop, get_loop
from app.logging import gCon

import tests.adelphoi_test_config as tconf
import app.sdc.s_utils as su
from app.sdc.Dependencies import Dependencies
#import copy


@pytest.fixture
def sync1():

    #conf = copy.deepcopy(tconf.test_routable_kernel)
    #conf['modules'][0]['args'] = ( tc.FLAG_1, )

    kernel_conf = yaml.safe_load(tconf.testable_routable_kernel_template)
    kernel = su.boot_kernel('testsync', kernel_conf)

    #aroutable = kernel.get_dep(Dependencies.ROUTER)
    #aroutable = TRoutable(tc.FLAG_1)
    app = SyncApp(tc.HOST_1, kernel)
    return app


@pytest.fixture
def sync2():

    #conf = copy.deepcopy(tconf.test_routable_kernel)
    #conf['modules'][0]['args'] = ( tc.FLAG_2, )
    kernel_conf = yaml.safe_load(tconf.testable_routable_kernel_template)
    kernel = su.boot_kernel('testsync2', kernel_conf)

    #aroutable = kernel.get_dep(Dependencies.ROUTER)
    #aroutable = TRoutable(tc.FLAG_2)
    app = SyncApp(tc.HOST_2, kernel)
    return app


def test_sync_route(sync1):

    test = SyncTester(sync1)
    with test:
        response = test.post("/inbox/lino", json = { 'msg' : 'do_all' })

        assert response.status_code == 200
        assert response.body == b'Hello lino! do_all'


def test_get_flag(sync1, sync2):

    test1 = SyncTester(sync1)
    test2 = SyncTester(sync2)

    with test1, test2:
        response = test1.post("/get_remote_flag", json = { 
                                          'dest' : tc.HOST_2,
                                          'msg' : 'flag1' })
    assert response.status_code == 200
    jsonres = json.loads(response.body)
    assert jsonres['flag'] == 'hello'


def test_get_flag_no(sync1, sync2):

    test1 = SyncTester(sync1)
    test2 = SyncTester(sync2)

    #with test1, test2, pytest.raises(Exception):
    response = test1.post("/get_remote_flag", json = { 
                                          'dest' : "www.nohost.com",
                                          'msg' : 'flag1' })
    assert (response.status_code == 401)

