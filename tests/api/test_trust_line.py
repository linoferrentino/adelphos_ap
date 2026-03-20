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
# testing trusti lines.


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


# to create a trust line I first test a local trust line, then a remote trust line,
# a remote is a trust line where the three aliases do not reside in the same instance.

adelphos_tl_test =  {"General": {
    "name" : '_test_adelphos_trust_lines',
    "debug": True, 
    "port": 9911, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    #"root_user": "@john_remote@localhost:5012", 
    "root_user": ":local:", 
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
    "host":  "localhost:5011", 
    "root_user": "@john_remote@localhost:5012", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$Odkr3o7V+SOVF6Dn5NB8XQ$NX9ZG6tqB4a/hQqEM6hvNnFsJt5VvCjbwuvYEU00f60"
    }, 
            "demo_users":
   [{"name": "john_remote", "alias": "##john.jf", "password": "john_tl"}, 
    {"name": "mary_remote", "alias": "##mary.mf", "password": "mary_tl"}]
}


@pytest.fixture(scope = "module")
def adelphos_remote_process_tl():
    server = ProcessServer()
    with server.run_in_subprocess(adelphos_remote_tl_conf):
        yield


@pytest.fixture(scope = "module")
#def adelphos_tl(adelphos_remote_process_tl):
def adelphos_tl():
    yield from tu.generator_test_client(adelphos_tl_test, True)


def create_trust_line(websocket):
    websocket.send_text('login alias ##alice.af  password alice_tl')
    data = websocket.receive_text()
    assert re.match('Login OK.*', data) is not None
    # OK, now I have logged in, I can try to create a family

    websocket.send_text('trust_line_create alias_to ##bob.bf judge ##carl.cf')
    data = websocket.receive_text()
    assert re.match("Trust line created", data) is not None


def test_create_trust_line(adelphos_tl):

    # I simulate a user that wants to login
    with adelphos_tl.websocket_connect("/api/ws") as websocket:
        create_trust_line(websocket)

