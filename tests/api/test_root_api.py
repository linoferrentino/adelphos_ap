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
# testing the root api


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



adelphos_root_api_test =  {"General": {
    "name" : '_test_adelphos_trust_lines',
    "debug": True, 
    "port": 9911, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    "root_user": ":local:", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users":
    [
        {"name": "john_root", "alias": "##john.fam", "password": "john00", "root" : True} 
    ]
}


@pytest.fixture(scope = "module")
def adelphos_root():
    yield from tu.generator_test_client(adelphos_root_api_test, False)


def test_execute_local_script(adelphos_root):
    # to test the local script first of all I have to open the backdoor.

    with adelphos_root.websocket_connect("/api/ws") as websocket:
        websocket.send_text('backdoor password super_secret')
        data = websocket.receive_text()
        assert data == 'Backdoor OK, you are root' 


