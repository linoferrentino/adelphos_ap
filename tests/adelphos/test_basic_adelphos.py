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


def test_basic1(get_routable_app):

    ad1 = get_routable_app('adelphos1', tconf.adelphos_stub,
                           tconf.adelphos_simple_conf)


def Xtest_basic2(get_standalone_app):
    ad1 = get_standalone_app('adelphos1', tconf.adelphos_stub,
                           tconf.adelphos_simple_conf)

    with ad1:
        port = tconf.adelphos_stub['General']['port']
        gCon.log(f"I want to connect to port {port}")
        response = httpx.post(f'http://127.0.0.1:{port}/api/users/adelphos/inbox', 
                              json = {'msg' : 'do_all'})
        assert response.status_code == 401


def test_basic2(get_standalone_app):
    ad1 = get_standalone_app('adelphos1', tconf.adelphos_stub,
                           tconf.adelphos_simple_conf)

    gCon.log(f"osi {ad1}")

    with ad1:
        gCon.log(f"osi 999 {ad1}")
        time.sleep(5)
        gCon.log("osi 2")
        port = tconf.adelphos_stub['General']['port']
        gCon.log(f"I want to connect to port {port}")
        response = httpx.post(f'http://127.0.0.1:{port}/api/users/adelphos/inbox', 
                              json = {'msg' : 'do_all'})
        assert response.status_code == 401


def Xtest_basic21(get_standalone_app):
    ad1 = get_standalone_app('adelphos1', tconf.adelphos_stub,
                           tconf.adelphos_simple_conf)

    with ad1:
        time.sleep(5)
        gCon.log("osi 2")
        port = tconf.adelphos_stub['General']['port']
        gCon.log(f"I want to connect to port {port}")
        response = httpx.post(f'http://127.0.0.1:{port}/api/users/adelphos/inbox', 
                              json = {'msg' : 'do_all'})
        assert response.status_code == 401



#def test_basic2(get_standalone_app):
#    ad1 = get_standalone_app('adelphos1', tconf.adelphos_stub,
#                           tconf.adelphos_simple_conf)
#
#    gCon.log("osi")
#
#    gCon.log(f"osi 1zz {ad1}")
#    time.sleep(5)
#    gCon.log("osi 2")
#    port = tconf.adelphos_stub['General']['port']
#    gCon.log(f"I want to connect to port {port}")
#    response = httpx.post(f'http://127.0.0.1:{port}/api/users/adelphos/inbox', 
#                          json = {'msg' : 'do_all'})
#    #assert response.status_code == 401



