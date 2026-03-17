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

import pytest
#from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient


#
## I can have several test instances that speak together.

# note that this session needs to speak to another instance.
#
adelphos_t1_test =  {"General": {
    "name" : "_test_adelphos_t1",
    "debug": True, 
    "port": 9911, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    "root_user": "@john_test@localhost:5011", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users":
   [{"name": "alice", "alias": "##alice.af", "password": "alice11"}, 
    {"name": "bob", "alias": "##bob.bf", "password": "bob11"}]
}

adelphos_slave1_conf =  {"General": {
    "name" : "_test_adelphos_remote1",
    "debug": True, 
    "port": 5011, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:5011", 
    "root_user": "@john_test@localhost:5011", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$Odkr3o7V+SOVF6Dn5NB8XQ$NX9ZG6tqB4a/hQqEM6hvNnFsJt5VvCjbwuvYEU00f60"
    }, 
            "demo_users":
   [{"name": "john_test", "alias": "##john.jf", "password": "john11"}, 
    {"name": "mary_test", "alias": "##mary.mf", "password": "mary11"}]
}


class ProcessServer:
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_subprocess(self):
        if mp.get_start_method() != 'spawn':
            mp.set_start_method('spawn')
        p = mp.Process(target = start_app_thread)
        p.start()
        try:
            yield
        finally:
            p.kill()
            p.join()


def start_app_thread():
    slave1_app = get_app('adelphos_slave1', None, adelphos_slave1_conf)
    uvicorn.run(slave1_app, host="127.0.0.1", port=5011, 
                            log_level="info")


@pytest.fixture(scope = "module")
def adelphos_slave_process2():
    server = ProcessServer()
    with server.run_in_subprocess():
        yield


@pytest.fixture(scope = "module")
def adelphos2(adelphos_slave_process2):
    # this first wait is needed to let the slave to come up
    gCon.log("first sleep to let the slave come up")
    time.sleep(1)
    client = TestClient(get_app('_test_adelphos_t1', None, adelphos_t1_test))
    with client:
        gCon.log("second sleep to let the root discovery")
        time.sleep(0.1)
        yield client


def atest_sub_proc_1(adelphos2, adelphos_slave_process2):
    # this second sleep is needed to let the root user discovery

    with adelphos2.websocket_connect("/api/ws") as websocket:
        websocket.send_text('login alias ##bob.bf password bob11')
        data = websocket.receive_text()
        assert re.match('Login OK.*', data) is not None


