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


import re
import httpx
import pytest
import httpx
import time
from httpx_ws import aconnect_ws

from app.core.AdelphosCoreException import AdelphosBaseException
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno
from app.exc.AdelphosException import AdErrno
from app.logging import gCon
from app.sdc.Dependencies import Dependencies
from tests.testers.fixtures import get_routable_app
from tests.testers.fixtures import get_standalone_app

import app.consts as CNST
import app.sdc.standard_conf as stdcnf
import tests.adelphoi_test_config as tconf
import tests.daemon.daemon_tests as dtests
import tests.social.social_tests as stests
import tests.t_utils as tu
import tests.alias_helpers as ah
import app.misc.alias_utils as au

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
                await tu.ws_assert_code_async(ws, AdErrno.EINVALID_SYNTAX)

                await ws.send_text("dbg.echo msg lino")
                await tu.ws_assert_res_str_async(ws, "hello lino!")


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


def test_get_daemon_cli(get_routable_app):
    test1 = get_routable_app('clitest', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)
    with test1:
        res = test1.get('/daemon_cli')
        assert (res.status_code == 200)
        match_instance = re.search('sync-clitest', res.body.decode())
        assert match_instance is not None


def test_create_root_user(get_routable_app):
    test1 = get_routable_app('test100', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)

    root_pass = tconf.adelphos_testable_1_conf['_root_password_']
    local_root = au.get_local_alias(tconf.adelphos_testable_1_conf['_root_handle_'])

    with test1, test1.websocket_connect(CNST.WS_ROUTE) as websocket:
        websocket.send_text(f"alias.login login root.admins password {root_pass}")
        data = tu.ws_assert_code(websocket, AdErrno.DONE_OK)
        gCon.log(f"now I will login as {local_root}")
        ah.ws_alias_login_in_app(test1, local_root, websocket, 
                                 'root.admins', root_pass)

        ah.ws_create_user_alias(test1, websocket, 'john', 'john.smith', 'john11')
 

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
            "alias.create name linoxferre password secret equity 10", user_ok)

        count_msg = user_ob.count_msg()
        assert count_msg == 1

        msg = user_ob.pop_lst_msg()
        assert ECoreErrno.EINVALID_ALIAS_SYNTAX == \
                AdelphosBaseException.parse_exc_str(msg.content)
        assert "linoxferre" == AdelphosBaseException.parse_detail(msg.content)

        stests.send_to_daemon_ctx(test1, test2, host2,
            "alias.create name lino.ferre password secret equity 10", user_ok)

        count_msg = user_ob.count_msg()
        assert count_msg == 1

        msg = user_ob.pop_lst_msg()
        assert msg.content == 'Alias created, you can login, now.'

        stests.send_to_daemon_ctx(test1, test2, host2,
            "alias.create name basso.ferre password secret99 equity 10", user_ok)

        count_msg = user_ob.count_msg()
        assert count_msg == 1

        msg = user_ob.pop_lst_msg()
        assert ECoreErrno.EDUPLICATED_FAMILY == \
                AdelphosBaseException.parse_exc_str(msg.content)


        with test2.websocket_connect(CNST.WS_ROUTE) as websocket:
            ah.ws_alias_login(user_ob, websocket, 'lino.ferre', 'secret')
            #websocket.send_text(f"alias.login login lino.ferre password secret")
            #tu.ws_assert_code(websocket, AdErrno.DONE_OK)

            #count_msg = user_ob.count_msg()
            #assert count_msg == 1

            #msg = user_ob.pop_lst_msg()
            #match_tk = re.match('Copy this command to finalize', msg.content)
            #assert match_tk is not None

            #token_tk = re.search(r"tk (.*)$", msg.content)
            #assert token_tk is not None
            #token = token_tk.group(1)
            #token = token[:-1]

            #websocket.send_text(f"alias.put_token tk {token}")
            #tu.ws_assert_code(websocket, AdErrno.DONE_OK)
 

def Xtest_real_remote_add_simple(get_routable_app):
    test1 = get_routable_app('test100', tconf.adelphos_stub, 
                                adelphos_standard_configuration)
    test2 = get_routable_app('test201', tconf.adelphos_t2_test,
                                adelphos_standard_configuration)

    host2 = tconf.adelphos_t2_test['General']['host']
    dtests._test_remote_add(test1, test2, host2)


