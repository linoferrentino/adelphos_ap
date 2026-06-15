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
from app.sdc.standard_conf import adelphos_standard_configuration
from app.logging import gCon
from tests.testers.fixtures import get_standalone_app
from tests.testers.fixtures import get_routable_app
#from tests.testers.fixtures import get_routable_app_TEST

from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport
import tests.social.social_tests as stests


def test_real1(get_standalone_app):
    ad1 = get_standalone_app('adelphos1', tconf.adelphos_t1_test,
                           adelphos_standard_configuration)

    with ad1:
        time.sleep(1)
        port = tconf.adelphos_t1_test['General']['port']
        gCon.log(f"I want to connect to port {port}")
        response = httpx.post(f'http://127.0.0.1:{port}/api/users/adelphos/inbox', 
                              json = {'msg' : 'do_all'})
        assert response.status_code == 405


@pytest.mark.anyio
async def test_real_sndmsg(get_standalone_app):

    ad1 = get_standalone_app('adelphos1', tconf.adelphos_t1_test,
                           adelphos_standard_configuration)

    ad2 = get_standalone_app('adelphos2', tconf.adelphos_t2_test,
                           adelphos_standard_configuration)

    with ad1, ad2:
        port = tconf.adelphos_t1_test['General']['port']
        async with httpx.AsyncClient() as client:
            async with aconnect_ws(f"http://localhost:{port}/api/ws", client) as ws:
                await ws.send_text("WHAT")
                datas = await ws.receive_text()
                assert datas == "WHAT: no such command"

                await ws.send_text("dbg.echo msg lino")
                datas = await ws.receive_text()
                assert datas == "hello lino!"


def test_post_real_kernel(get_routable_app):
    test1 = get_routable_app('test100', tconf.adelphos_stub, 
                                 adelphos_standard_configuration)
    test2 = get_routable_app('test201', tconf.adelphos_t2_test,
                             adelphos_standard_configuration)

    host2 = tconf.adelphos_t2_test['General']['host']
    stests._test_sndpost_to_host(test1, test2, host2, 'demo1', 'demo77')



