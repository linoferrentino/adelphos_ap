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
# the starting point of the adelphos test


from .AdelphosApp import get_app
from fastapi.testclient import TestClient
from app.logging import gCon
from fastapi.websockets import WebSocket
from contextlib import asynccontextmanager
import re
from fastapi import FastAPI
import pytest
import time
import threading
import uvicorn


#
## I can have several test instances that speak together.
#
adelphos_t1_test =  {"General": {
    "debug": True, 
    "port": 9911, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    "root_user": "@john_test@localhost:5011", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$Odkr3o7V+SOVF6Dn5NB8XQ$NX9ZG6tqB4a/hQqEM6hvNnFsJt5VvCjbwuvYEU00f60"
    }, 
            "demo_users":
   [{"name": "alice", "alias": "##alice.af", "password": "alice11"}, 
    {"name": "bob", "alias": "##bob.bf", "password": "bob11"}]
}


@pytest.fixture(scope = "session")
def adelphos1():
    client = TestClient(get_app('adelphos_t1', None, adelphos_t1_test))
    with client:
        yield client


def test_ad_1(adelphos1):

    with adelphos1.websocket_connect("/api/ws") as websocket:
        websocket.send_text('login alias ##bob.bf password bob11')
        data = websocket.receive_text()
        assert re.match('Login OK.*', data) is not None


def test_ad_2(adelphos1):

    with adelphos1.websocket_connect("/api/ws") as websocket:
        websocket.send_text('login alias ##john.jf password john12')
        data = websocket.receive_text()
        assert re.match('User error: Invalid username/password', data) is not None


def test_ad_3(adelphos1):

    with adelphos1.websocket_connect("/api/ws") as websocket:
        websocket.send_text('backdoor alias ##root.admins password super_secret')
        data = websocket.receive_text()
        assert data == 'Backdoor OK, you are root' 


