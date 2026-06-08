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


import httpx

from tests.testers.fixtures import get_routable_app
from tests.testers.fixtures import get_standalone_app
import tests.adelphoi_test_config as tconf
from app.logging import gCon
import time
import json


def test_basic1(get_routable_app):

    ad1 = get_routable_app('adelphos1', tconf.adelphos_stub,
                           tconf.adelphos_simple_conf)


def test_basic2(get_standalone_app):
    ad1 = get_standalone_app('adelphos1', tconf.adelphos_stub,
                           tconf.adelphos_simple_conf)

    with ad1:
        time.sleep(1)
        port = tconf.adelphos_stub['General']['port']
        gCon.log(f"I want to connect to port {port}")
        response = httpx.post(f'http://127.0.0.1:{port}/api/users/adelphos/inbox', 
                              json = {'msg' : 'do_all'})
        assert response.status_code == 401


def test_comm(get_standalone_app):

    ad1 = get_standalone_app('adelphos1', tconf.adelphos_stub,
                           tconf.adelphos_simple_conf)

    ad2 = get_standalone_app('adelphos2', tconf.adelphos_t2_test,
                           tconf.adelphos_simple_conf)

    port = tconf.adelphos_stub['General']['port']
    host2 = tconf.adelphos_t2_test['General']['host']
    port2 = tconf.adelphos_t2_test['General']['port']

    with ad1, ad2:
        response = httpx.post(f'http://127.0.0.1:{port}/api/_backdoor', 
             json = {'msg' : f'discover_uri uri http://{host2}/api/users/demo77'})
        assert response.status_code == 202


def test_sync_comm(get_routable_app):

    test1 = get_routable_app('test1', tconf.adelphos_stub, 
                                 tconf.adelphos_simple_conf)
    test2 = get_routable_app('test2', tconf.adelphos_t2_test,
                             tconf.adelphos_simple_conf)

    port = tconf.adelphos_stub['General']['port']
    host2 = tconf.adelphos_t2_test['General']['host']
    response = test1.post(f'/_backdoor', 
        json = {'msg' : f'discover_uri uri https://{host2}/api/users/demo77'})
    assert response.status_code == 202
    body_str = response.body
    body_ob = json.loads(body_str)
    assert body_ob['id'] == f"https://{host2}/api/users/demo77"
    


