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
import pytest

from tests.testers.fixtures import get_routable_app
from tests.testers.fixtures import get_routable_app_param
from tests.testers.fixtures import get_standalone_app
import tests.adelphoi_test_config as tconf
from app.logging import gCon
import time
import json


def test_basic1(get_routable_app_param):

    ad1 = get_routable_app_param('adelphos1', tconf.testable_debug_kernel_template,
                           tconf.adelphos_testable_1_conf)


def test_basic2(get_standalone_app):

    ad1 = get_standalone_app('adelphos1', tconf.testable_debug_kernel_template,
                           tconf.adelphos_testable_1_conf)

    with ad1:
        time.sleep(2)
        port = tconf.adelphos_testable_1_conf['_port_']
        gCon.log(f"I want to connect to port {port}")
        response = httpx.post(f'http://127.0.0.1:{port}/api/users/adelphos/inbox', 
                              json = {'msg' : 'do_all'})
        assert response.status_code == 401


def test_comm(get_standalone_app):

    ad1 = get_standalone_app('adelphos1', tconf.testable_debug_kernel_template,
                           tconf.adelphos_testable_1_conf)

    ad2 = get_standalone_app('adelphos2', tconf.testable_debug_kernel_template,
                           tconf.adelphos_testable_2_conf)

    port = tconf.adelphos_testable_1_conf['_port_']
    port2 = tconf.adelphos_testable_2_conf['_port_']
    host2 = f"localhost:{port2}"

    with ad1, ad2:
        time.sleep(3)
        response = httpx.post(f'http://127.0.0.1:{port}/api/_backdoor', 
             json = {'msg' : f'discover_uri uri http://{host2}/api/users/demo77'})
        assert response.status_code == 202



def test_sync_comm(get_routable_app):

    test1 = get_routable_app('test1', tconf.testable_debug_kernel_template, 
                        conf = tconf.adelphos_testable_1_conf)
    test2 = get_routable_app('test2', tconf.testable_debug_kernel_template,
                        conf = tconf.adelphos_testable_2_conf)

    with test1, test2:

        port = tconf.adelphos_testable_1_conf['_port_']
        port2 = tconf.adelphos_testable_2_conf['_port_']
        host2 = f"localhost:{port2}"
        response = test1.post(f'/_backdoor', 
            json = {'msg' : f'discover_uri uri https://{host2}/api/users/demo77'})
        assert response.status_code == 202
        body_str = response.body
        body_ob = json.loads(body_str)
        assert body_ob['id'] == f"https://{host2}/api/users/demo77"
        


