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
import httpx
import time

import tests.adelphoi_test_config as tconf
import tests.adelphoi_build_config as bconf

#from app.sdc.standard_conf import adelphos_standard_configuration
from app.logging import gCon
from tests.testers.fixtures import get_standalone_app
from tests.testers.fixtures import get_routable_app
#from tests.testers.fixtures import get_routable_app_TEST

from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport
import tests.social.social_tests as stests
import tests.daemon.daemon_tests as dtests
from app.exc.AdelphosException import parse_exc_str
from app.exc.AdelphosException import AdErrno

import app.sdc.standard_conf as stdcnf


def test_real1(get_standalone_app):
    ad1 = get_standalone_app('adelphos1', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)
    with ad1:
        time.sleep(2)
        port = tconf.adelphos_testable_1_conf['_port_']
        gCon.log(f"I want to connect to port {port}")
        response = httpx.post(f'http://127.0.0.1:{port}/api/users/adelphos/inbox', 
                              json = {'msg' : 'do_all'})
        assert response.status_code == 405


@pytest.mark.anyio
async def test_real_sndmsg(get_standalone_app):

    ad1 = get_standalone_app('adelphos1', stdcnf.release_kernel_template,
                            tconf.adelphos_testable_1_conf)

    ad2 = get_standalone_app('adelphos2', stdcnf.release_kernel_template,
                            tconf.adelphos_testable_2_conf)

    with ad1, ad2:
        time.sleep(4)
        port = tconf.adelphos_testable_1_conf['_port_']
        async with httpx.AsyncClient() as client:
            async with aconnect_ws(f"http://localhost:{port}/api/ws", client) as ws:
                await ws.send_text("WHAT")
                datas = await ws.receive_text()
                assert AdErrno.EINVALID_SYNTAX == parse_exc_str(datas)

                await ws.send_text("dbg.echo msg lino")
                datas = await ws.receive_text()
                assert datas == "hello lino!"


def test_post_real_kernel(get_routable_app):
    test1 = get_routable_app('adelphos1', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)

    test2 = get_routable_app('adelphos2', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_2_conf)

    port2 = tconf.adelphos_testable_2_conf['_port_']
    host2 = f'localhost:{port2}'
    stests._test_sndpost_to_host(test1, test2, host2, 'demo1', 'demo77', 'demo1')



def test_real_remote_add(get_routable_app):
    test1 = get_routable_app('test100', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)
    test2 = get_routable_app('test201', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_2_conf)

    port2 = tconf.adelphos_testable_2_conf['_port_']
    host2 = f'localhost:{port2}'
    dtests._test_remote_add(test1, test2, host2,
                            AdErrno.EREMOTE_ADELPHOS_UNAUTHORIZED)


def test_real_alias_create(get_routable_app):
    test1 = get_routable_app('test101', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)
    test2 = get_routable_app('test202', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_2_conf)

    port2 = tconf.adelphos_testable_2_conf['_port_']
    host2 = f'localhost:{port2}'

    stests._send_to_daemon(test1, test2, host2,
        "alias.create name lino.ferre password secret", 'demo1')


def Xtest_real_remote_add_simple(get_routable_app):
    test1 = get_routable_app('test100', tconf.adelphos_stub, 
                                adelphos_standard_configuration)
    test2 = get_routable_app('test201', tconf.adelphos_t2_test,
                                adelphos_standard_configuration)

    host2 = tconf.adelphos_t2_test['General']['host']
    dtests._test_remote_add(test1, test2, host2)


