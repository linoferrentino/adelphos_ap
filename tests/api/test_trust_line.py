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


from app.AdelphosApp import get_app
from app.AdelphosApp import del_app
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
#from app.api.AdelphosException import EAdelhposErrno


# to create a trust line I first test a local trust line, then a remote trust line,
# a remote is a trust line where the three aliases do not reside in the same instance.

adelphos_tl_test =  {"General": {
    "name" : '_test_adelphos_trust_lines',
    "debug": True, 
    "port": 9911, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    "root_user": "@john_remote@localhost:5012", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users":
    [{"name": "alice", "alias": "##alice.af", "password": "alice_tl", "root" : True}, 
    {"name": "bob", "alias": "##bob.bf", "password": "bob_tl"},
    {"name": "carl", "alias": "##carl.cf", "password": "carl_tl"}
    ]
}

adelphos_remote_tl_conf =  {"General": {
    "name" : '_test_adelphos_remote_tl',
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
def adelphos_remote_process_tl():
    server = ProcessServer()
    with server.run_in_subprocess(adelphos_remote_tl_conf):
        yield


@pytest.fixture(scope = "module")
def adelphos_tl(adelphos_remote_process_tl):
    yield from tu.generator_test_client(adelphos_tl_test, True)


def OLDAP_test_check_carl(adelphos_tl):
    with adelphos_tl.websocket_connect("/api/ws") as websocket:
        websocket.send_text('al_login1f alias ##carl.cf  password carl_tl')
        tu.websocket_assert_code(websocket, EAdelhposErrno.DONE_OK)


def create_trust_line(websocket, alias_to, code = 0):
    websocket.send_text('al_login1f alias ##alice.af  password alice_tl')
    tu.websocket_assert_code(websocket, EAdelhposErrno.DONE_OK)

    websocket.send_text(f'trust_line_create alias_to {alias_to} referee ##carl.cf')
    tu.websocket_assert_code(websocket, code)


def OLDAP_test_create_trust_line(adelphos_tl):

    # I simulate a user that wants to login
    with adelphos_tl.websocket_connect("/api/ws") as websocket:
        create_trust_line(websocket, '##bob.bf' , EAdelhposErrno.DONE_OK)


# this cannot work, now, because we have the need of two independent instances.
def XXtest_create_trust_line_remote(adelphos_tl):

    with adelphos_tl.websocket_connect("/api/ws") as websocket:
        create_trust_line(websocket, '##john.jf@localhost:5012',
                          EAdelhposErrno.EURI_NOT_FOUND)


def OLDAP_test_create_tl_rem_root(adelphos_tl):

    script = [
            'backdoor password super_secret',
            'sudo_adelphos_allow remote_adelphos localhost:5012',
            'sudo_su_push alias ##alice.af',
            'sudo_su_pop'
            ]
    tu.play_script_on_instance_OK(adelphos_tl, script)

