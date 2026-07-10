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

from app.sdc.Dependencies import Dependencies
import tests.adelphoi_test_config as tconf
import tests.adelphoi_build_config as bconf

#from app.sdc.standard_conf import adelphos_standard_configuration
from app.logging import gCon
from tests.testers.fixtures import get_standalone_app
from tests.testers.fixtures import get_routable_app
#from tests.testers.fixtures import get_routable_app_TEST

from httpx_ws import aconnect_ws
#from httpx_ws.transport import ASGIWebSocketTransport
import tests.social.social_tests as stests
import tests.daemon.daemon_tests as dtests
from app.exc.AdelphosException import parse_exc_str
from app.exc.AdelphosException import AdErrno

from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno

import app.sdc.standard_conf as stdcnf
from app.core.AdelphosCoreException import AdelphosBaseException


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


@pytest.mark.anyio
async def test_real_alias_create_async(get_standalone_app):

    ad1 = get_standalone_app('adelphos11', stdcnf.release_kernel_template,
                            tconf.adelphos_testable_1_conf)

    ad2 = get_standalone_app('adelphos21', stdcnf.release_kernel_template,
                            tconf.adelphos_testable_2_conf)

    port2 = tconf.adelphos_testable_2_conf['_port_']
    host2 = f"localhost:{port2}"
    with ad1, ad2:
        time.sleep(4)
        port = tconf.adelphos_testable_1_conf['_port_']
        async with httpx.AsyncClient() as client:
            async with aconnect_ws(f"http://localhost:{port}/api/ws", client) as ws:
                await ws.send_text(
f"dbg.sndpost to @adelphos@{host2} msg 'alias.create name lino.ferre password test99' \
from demo1")
            time.sleep(1)


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


def test_real_alias_create_sync(get_routable_app):
    test1 = get_routable_app('test101', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)
    test2 = get_routable_app('test202', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_2_conf)

    port2 = tconf.adelphos_testable_2_conf['_port_']
    host2 = f'localhost:{port2}'

    user_ok = 'demo1'

    with test1, test2:

        user_ob = test1.app.routable.get_dep(
                Dependencies.SOCIAL).login_user(user_ok)

        stests.send_to_daemon_ctx(test1, test2, host2,
            "alias.create name linoxferre password secret", user_ok)

        count_msg = user_ob.count_msg()
        assert count_msg == 1

        msg = user_ob.pop_lst_msg()
        #assert msg.content == 'Adelphos core error #3# linoxferre'
        assert ECoreErrno.EINVALID_ALIAS_SYNTAX == \
                AdelphosBaseException.parse_exc_str(msg.content)
        assert "linoxferre" == AdelphosBaseException.parse_detail(msg.content)

        stests.send_to_daemon_ctx(test1, test2, host2,
            "alias.create name lino.ferre password secret", user_ok)

        count_msg = user_ob.count_msg()
        assert count_msg == 1

        msg = user_ob.pop_lst_msg()
        assert msg.content == 'Alias created, you can login, now.'


def Xtest_real_remote_add_simple(get_routable_app):
    test1 = get_routable_app('test100', tconf.adelphos_stub, 
                                adelphos_standard_configuration)
    test2 = get_routable_app('test201', tconf.adelphos_t2_test,
                                adelphos_standard_configuration)

    host2 = tconf.adelphos_t2_test['General']['host']
    dtests._test_remote_add(test1, test2, host2)


