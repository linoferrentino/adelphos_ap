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

    kernel_build = tconf.testable_routable_kernel_template.format(
            _flag_ = tc.FLAG_1 )

    kernel_conf = yaml.safe_load(kernel_build)
    kernel = su.boot_kernel('testsync', kernel_conf)

    app = SyncApp(tc.HOST_1, kernel)
    return app


@pytest.fixture
def sync2():

    kernel_build = tconf.testable_routable_kernel_template.format(
            _flag_ = tc.FLAG_2 )

    kernel_conf = yaml.safe_load(kernel_build)
    kernel = su.boot_kernel('testsync2', kernel_conf)

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
        assert jsonres['flag'] == tc.FLAG_2

        response = test1.post("/get_remote_flag", json = { 
                                          'dest' : tc.HOST_1,
                                          'msg' : 'flag1' })

        assert response.status_code == 200
        jsonres = json.loads(response.body)
        assert jsonres['flag'] == tc.FLAG_1 


def test_get_flag_no(sync1, sync2):

    test1 = SyncTester(sync1)
    test2 = SyncTester(sync2)

    with test1, test2:
        response = test1.post("/get_remote_flag", json = { 
                                          'dest' : "www.nohost.com",
                                          'msg' : 'flag1' })
    assert (response.status_code == 401)

