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
from .AdelphosApp import del_app
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
#from tests.ProcessServer import mp_set_start_method

import pytest
#from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient


#
## I can have several test instances that speak together.

adelphos_t2_test =  {"General": {
    "name" : "_test_adelphos_t2",
    "debug": True, 
    "port": 9911, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    "root_user": ":local:", 
    # the password for alice is dual, one is for her being a normal alias in adelphos,
    # the other as a super user, the super user does not participate in the transactions
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users": [
    {"name": "alice99", "alias": "##alice.af", "password": "alice11", "root" : True}, 
    {"name": "bobzz", "alias": "##bob2.bf", "password": "bob22"}]
}

adelphos_remote2_conf  =  {"General": {
    "name" : "_test_adelphos_remote2",
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


@pytest.fixture(scope = "module")
def adelphos_remote2_process():
    server = ProcessServer()
    with server.run_in_subprocess(adelphos_remote2_conf):
        yield


# this generator will be moved in the test module, this is without wait
def generator_test_client(instance_conf, must_wait = False):

    if must_wait:
        gCon.log("first sleep to let the slave come up")
        time.sleep(1.2)
    client = TestClient(get_app(instance_conf['General']['name'], None, instance_conf))
    with client:
        if must_wait:
            gCon.log("second sleep to let the root discovery")
            time.sleep(0.5)
        yield client
    del_app()


@pytest.fixture(scope = "module")
def adelphos2():
    yield from generator_test_client(adelphos_t2_test)
 

def test_backdoor_local(adelphos2):

    with adelphos2.websocket_connect("/api/ws") as websocket:
        websocket.send_text('backdoor alias ##root.admins password super_secret')
        data = websocket.receive_text()
        assert data == 'Backdoor OK, you are root' 

    gCon.log("Done!")



def test_sub_proc_2(adelphos2):

    with adelphos2.websocket_connect("/api/ws") as websocket:
        websocket.send_text('login alias ##bob2.bf password bob22')
        data = websocket.receive_text()
        assert re.match('Login OK.*', data) is not None


