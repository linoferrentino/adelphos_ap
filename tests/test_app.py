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


from app.AdelphosApp import get_app
from app.AdelphosApp import del_app
from fastapi.testclient import TestClient
from app.logging import gCon
from fastapi.websockets import WebSocket
from contextlib import asynccontextmanager
import re
from fastapi import FastAPI
import multiprocessing as mp
import pytest
import time
import threading
import uvicorn
import contextlib
import time
import threading
import uvicorn
import asyncio
#import pytest_asyncio
import httpx
from tests.ProcessServer import ProcessServer
import tests.t_utils as tu

import pytest
#from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from app.api.AdelphosException import EAdelhposErrno


#
## I can have several test instances that speak together.

# note that this session needs to speak to another instance.
#
adelphos_t1_test =  {"General": {
    "name" : '_test_adelphos_t1',
    "debug": True, 
    "port": 9911, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    "root_user": "@john_remote@localhost:5011", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users":
   [{"name": "alice", "alias": "##alice.af", "password": "alice11"}, 
    {"name": "bob", "alias": "##bob.bf", "password": "bob11"}]
}

adelphos_remote_1_conf =  {"General": {
    "name" : '_test_adelphos_remote1',
    "debug": True, 
    "port": 5011, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:5011", 
    "root_user": "@john_remote@localhost:5011", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$Odkr3o7V+SOVF6Dn5NB8XQ$NX9ZG6tqB4a/hQqEM6hvNnFsJt5VvCjbwuvYEU00f60"
    }, 
            "demo_users":
   [{"name": "john_remote", "alias": "##john.jf", "password": "john11"}, 
    {"name": "mary_remote", "alias": "##mary.mf", "password": "mary11"}]
}


@pytest.fixture(scope = "module")
def adelphos_remote_process():
    server = ProcessServer()
    with server.run_in_subprocess(adelphos_remote_1_conf):
        yield


@pytest.fixture(scope = "module")
def adelphos1(adelphos_remote_process):
    yield from tu.generator_test_client(adelphos_t1_test, True)


def test_sub_proc(adelphos1, adelphos_remote_process):
    # this second sleep is needed to let the root user discovery

    with adelphos1.websocket_connect("/api/ws") as websocket:
        websocket.send_text('login alias ##bob.bf password bob11')
        tu.websocket_assert_code(websocket, EAdelhposErrno.DONE_OK)


def test_ad_2(adelphos1, adelphos_remote_process):

    with adelphos1.websocket_connect("/api/ws") as websocket:
        websocket.send_text('login alias ##john.jf password john12')
        tu.websocket_assert_code(websocket, EAdelhposErrno.EINVALID_USER_OR_PASSWORD)


def test_ad_3(adelphos1, adelphos_remote_process):

    with adelphos1.websocket_connect("/api/ws") as websocket:
        websocket.send_text('backdoor password super_secret')
        tu.websocket_assert_code(websocket, EAdelhposErrno.DONE_OK)


# I can login as an activity pub to the instance, this is done off-the-grid, as
# we do not use a documented API

# I should be able to login to the instance as an activity pub user.
def test_login_ap(adelphos1):

    response = adelphos1.post('/_backdoor_api_/login', json = { 'user' : 'alice'})
    assert response.status_code == 200
    assert response.json() == { 'res' : 0 }

    # I cannot send here a post message because the recipient will fetch from
    # me the private key and this is not possible because I am not really a server.



# this will test the login in the remote , the remote is in another process so I
# have to make a normal call
def test_login_remote(adelphos1):

    response = httpx.post('http://localhost:5011/_backdoor_api_/login', json = {'user' : 'mary_remote'})
    assert response.status_code == 200
    assert response.json() == { 'res' : 0 }


    # after this I could login to the remote adelphos.
    gCon.log("-==========================================================")

    mention = '@daemon@localhost:5011'
    response = httpx.post('http://localhost:5011/_backdoor_api_/post', json = { 
        'recipient' : f"{mention}", 'msg' : 
        'alias_create alias ##mary_remote.family1 password mary99' })
    assert response.status_code == 200
    assert response.json() == { 'res' : 0 }

    # sleep a little to let the server get the message
    time.sleep(0.5)

    # now I read the unread messages.
    response = httpx.post('http://localhost:5011/_backdoor_api_/get_unread_messages', 
                          json = { 'how_many' : 1})
    assert response.status_code == 200
    assert response.json() == { 'res' : 
      [ 'Created alias ##mary_remote.family1 successfully. You can login, now.'] }





