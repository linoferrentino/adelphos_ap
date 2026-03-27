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
# testing trust lines.


from app.AdelphosApp import get_existent_app
from app.ad_api.AdDaemonApi import AdDaemonApi
from fastapi.testclient import TestClient
from app.logging import gCon
from fastapi.websockets import WebSocket
import re
from fastapi import FastAPI
import pytest
import time
from tests.ProcessServer import ProcessServer
import tests.t_utils as tu
import pytest
from app.api.AdelphosException import EAdelhposErrno

import httpx
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport


# to create a trust line I first test a local trust line, then a remote trust line,
# a remote is a trust line where the three aliases do not reside in the same instance.

adelphos_ad_api_test =  {"General": {
    "name" : '_test_adelphos_ad_api',
    "debug": True, 
    "port": 9911, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    "root_user": "@john_remote@localhost:5012", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users":
    [{"name": "alice", "alias": "##alice.tapif", "password": "alice_tapif", "root" : True}, 
    {"name": "bob_19", "alias": "##bob.bf19", "password": "bob_19"},
    {"name": "carl", "alias": "##carl.cf", "password": "carl_tl"}
    ]
}

adelphos_remote_ad_api =  {"General": {
    "name" : '_test_adelphos_remote_ad_api',
    "debug": True, 
    "port": 5012, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:5012", 
    "root_user": "@john_remote@localhost:5012", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$Odkr3o7V+SOVF6Dn5NB8XQ$NX9ZG6tqB4a/hQqEM6hvNnFsJt5VvCjbwuvYEU00f60"
    }, 
            "demo_users":
   [{"name": "john_remote", "alias": "##john.jf", "password": "john_tl"}, 
    {"name": "mary_remote", "alias": "##mary.mf", "password": "mary_tl"},
    {"name": "jean_remote", "alias": "##jean.jean_fam", "password": "jean_tl"},
    ]
}


@pytest.fixture(scope = "module")
def adelphos_remote_process_ad_api():
    server = ProcessServer()
    with server.run_in_subprocess(adelphos_remote_ad_api):
        yield


#@pytest.fixture(scope = "module")
#def adelphos_ad_api(adelphos_remote_process_ad_api):
#    yield from tu.generator_test_client(adelphos_ad_api_test, True)


@pytest.fixture(scope = "module")
def adelphos_ad_api(adelphos_remote_process_ad_api):
    time.sleep(1)
    server = ProcessServer()
    with server.run_in_subprocess(adelphos_ad_api_test):
        time.sleep(1.5)
        yield
        


# I have to use the backdoor api
@pytest.mark.anyio
async def test_check_echo(adelphos_ad_api):


    async with httpx.AsyncClient() as client:
        async with aconnect_ws("http://localhost:9911/api/ws", client) as ws:

            script_no_login = [
                ('test_recho msg "hello world" remote_instance localhost:5012',
                 EAdelhposErrno.ENOLOGIN)
            ]

            gCon.log('script 1')
            await tu.play_script_ws_async(ws, script_no_login)

            script_login = [
                ('al_login1f alias ##bob.bf19  password bob_19', 
                 EAdelhposErrno.DONE_OK),
                ('test_recho msg "hello world" remote_instance localhost:5012',
                 EAdelhposErrno.ENO_DAEMON_FOR_HOST)
            ]

            gCon.log('script 2')
            await tu.play_script_ws_async(ws, script_login)

            script_allow = [
    ('backdoor password super_secret', EAdelhposErrno.DONE_OK),
    ('sudo_adelphos_allow remote_adelphos localhost:5012', EAdelhposErrno.DONE_OK),
    ('sudo_su_push alias ##bob.bf19', EAdelhposErrno.DONE_OK),
    ('test_recho msg "this works" remote_instance localhost:5012', 
     EAdelhposErrno.ENO_DAEMON_FOR_HOST)
            ]

            gCon.log('script 3')
            await tu.play_script_ws_async(ws, script_allow)


    # Now I authorize the adelphos on the other side.
    async with httpx.AsyncClient() as client:
        async with aconnect_ws("http://localhost:5012/api/ws", client) as ws:

            script_allow = [
    ('backdoor password super_secret', EAdelhposErrno.DONE_OK),
    ('sudo_adelphos_allow remote_adelphos localhost:9911', EAdelhposErrno.DONE_OK),
    ('sudo_su_push alias ##mary.mf', EAdelhposErrno.DONE_OK),
    ('test_recho msg "this works" remote_instance localhost:9911', 
     'hello_remote this works')
            ]

            gCon.log('script ///////////////////////// FROM REMOTE')
            await tu.play_script_ws_async(ws, script_allow)



def xtest_check_echo(adelphos_ad_api):

    # to test the adelphos api I fake an encapsulated message and I give it
    # to my app
    with adelphos_ad_api.websocket_connect("/api/ws") as websocket:
        websocket.send_text('test_recho msg "hello world" remote_instance localhost:5012')
        tu.websocket_assert_code(websocket, EAdelhposErrno.ENO_DAEMON_FOR_HOST)

        # allow the instance
        script = [
            'backdoor password super_secret',
            'sudo_adelphos_allow remote_adelphos localhost:5012',
            'sudo_su_push alias ##alice.tapif',
            ]
        tu.play_script_on_instance_OK(adelphos_ad_api, script)
        websocket.send_text('test_recho msg "hello world" remote_instance localhost:5012')
        tu.websocket_assert_payload_success(websocket, 
          'hello world ##alice.tapif@localhost:9911 from localhost:5012')
