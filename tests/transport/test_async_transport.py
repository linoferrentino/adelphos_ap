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
import httpx
import time
import json

import tests.adelphoi_test_config as tconf
from app.transport.async_mode.AsyncTransport import AsyncTransport
from tests.transport.TRoutable import TRoutable
from app.transport.async_mode.StarletteWrap import StarletteWrap
from starlette.testclient import TestClient
from tests.testers.ProcessWrapper import ProcessWrapper
from app.logging import gCon
from app.sdc.Dependencies import Dependencies
import app.sdc.s_utils as su

PORT1 = 5999
PORT2 = 5997



@pytest.fixture
def app_t1():

    kernel = su.build_kernel('test1', tconf.test_routable_kernel)

    #aroutable = TRoutable("test")
    aroutable = kernel.get_dep(Dependencies.ROUTER)
    app = StarletteWrap(routable = aroutable)
    return app


@pytest.fixture(scope = "module")
def remote_app1():
    server = ProcessWrapper()
    with server.run_in_subprocess(su.build_kernel, ("rem1", 
                          tconf.test_routable_kernel), PORT1):
        time.sleep(2)
        yield


@pytest.fixture(scope = "module")
def remote_app2():
    server = ProcessWrapper()
    with server.run_in_subprocess(su.build_kernel, ("rem2", 
                tconf.test_routable_kernel), PORT2):
        time.sleep(2)
        yield


def test_async_route(app_t1):

    test = TestClient(app_t1) 
    
    response = test.post("/inbox/lino", json = { 'msg' : 'do_all' })

    assert response.status_code == 200
    assert response.content == b'Hello lino! do_all'


def test_remote_async(remote_app1):

    response = httpx.post('http://127.0.0.1:5999/inbox/lino', json = {'msg' : 'do_all'})
    assert response.status_code == 200
    assert response.content == b'Hello lino! do_all'


def test_async_comm(remote_app1, remote_app2):

    response = httpx.post(f'http://127.0.0.1:{PORT1}/get_remote_flag', 
                         json = {
                             'dest' : f'127.0.0.1:{PORT2}',
                             'msg' : 'flag1'})

    assert response.status_code == 200
    jsonres = json.loads(response.content)
    assert jsonres['flag'] == 'hello'
