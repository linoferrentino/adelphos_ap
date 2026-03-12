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
import contextlib
import time
import threading
import uvicorn



#
## I can have several test instances that speak together.

# note that this session needs to speak to another instance.
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

adelphos_slave1_conf =  {"General": {
    "debug": True, 
    "port": 5011, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:5011", 
    "root_user": ":local:", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$Odkr3o7V+SOVF6Dn5NB8XQ$NX9ZG6tqB4a/hQqEM6hvNnFsJt5VvCjbwuvYEU00f60"
    }, 
            "demo_users":
   [{"name": "john_test", "alias": "##john.jf", "password": "john11"}, 
    {"name": "mary_test", "alias": "##mary.mf", "password": "mary11"}]
}


@pytest.fixture(scope = "session")
def adelphos1():
    client = TestClient(get_app('adelphos_t1', None, adelphos_t1_test))
    with client:
        yield client


#class Server(uvicorn.Server):
#    def install_signal_handlers(self):
#        pass
#
#    @contextlib.contextmanager
#    def run_in_thread(self):
#        thread = threading.Thread(target=self.run)
#        thread.start()
#        try:
#            while not self.started:
#                time.sleep(1e-3)
#            yield
#        finally:
#            self.should_exit = True
#            thread.join()


def start_app_thread():
    slave1_app = get_app('adelphos_slave1', None, adelphos_slave1_conf)
    uvicorn.run(slave1_app, host="127.0.0.1", port=5011, 
                            log_level="info")

import multiprocessing as mp


@pytest.fixture(scope = "session")
def adelphos_slave1_th():
    mp.set_start_method('spawn')
    p = mp.Process(target = start_app_thread)
    p.start()
    yield

    #server_thread = threading.Thread(target=start_app_thread, daemon=True)
    #server_thread.start()
    #yield


@pytest.fixture(scope = "session")
def adelphos_slave1_back():
    slave1_app = get_app('adelphos_slave1', None, adelphos_slave1_conf)
    config = uvicorn.Config(slave1_app, host="127.0.0.1", port=5011, 
                            log_level="info")
    server = Server(config=config)
    with server.run_in_thread():
        yield


def test_ad_1(adelphos1, adelphos_slave1_th):

    #time.sleep(2)

    with adelphos1.websocket_connect("/api/ws") as websocket:
        websocket.send_text('login alias ##bob.bf password bob11')
        data = websocket.receive_text()
        assert re.match('Login OK.*', data) is not None


def xtest_ad_2(adelphos1):

    with adelphos1.websocket_connect("/api/ws") as websocket:
        websocket.send_text('login alias ##john.jf password john12')
        data = websocket.receive_text()
        assert re.match('User error: Invalid username/password', data) is not None


def xtest_ad_3(adelphos1):

    with adelphos1.websocket_connect("/api/ws") as websocket:
        websocket.send_text('backdoor alias ##root.admins password super_secret')
        data = websocket.receive_text()
        assert data == 'Backdoor OK, you are root' 


# I have to be able to build an activity pub post message in order to test the create
# alias


# I can login as an activity pub to the instance, this is done off-the-grid, as
# we do not use a documented API

# I should be able to login to the instance as an activity pub user.
def xtest_login_ap(adelphos1):

    response = adelphos1.post('/_backdoor_api_/login', json = { 'user' : 'alice'})
    assert response.status_code == 200
    gCon.rule("-------")
    gCon.log(response.json)
    assert response.json() == { 'login' : 'it works, alice' }


def atest_create_user(adelphos1):

    # I have to connect to the post route, and give a message to daemon
    res = adelphos1.post('/users/daemon/inbox', json = { 'msg' : 'hello' })




