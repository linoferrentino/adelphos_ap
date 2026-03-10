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
    "root_user": "@john@localhost:5011", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$QK8nKJOBQX0jU+S9fwJpLw$0wV4hG/ar/uJSlcDd4IV6bqEBLWz+rFLFBpuGiyaPjM"}, 
            "demo_users":
   [{"name": "john", "alias": "##john.jf", "password": "john11"}, 
    {"name": "mary", "alias": "##mary.mf", "password": "mary11"}]
}

adelphos_slave_instance =  {"General": {
    "debug": True, 
    "port": 8001, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    "root_user": ":local:", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$QK8nKJOBQX0jU+S9fwJpLw$0wV4hG/ar/uJSlcDd4IV6bqEBLWz+rFLFBpuGiyaPjM"}, 
            "demo_users":
   [{"name": "john", "alias": "##john.admins", "password": "john11"}, 
    {"name": "mary", "alias": "##mary.mf", "password": "mary11"}]
}


def uvicorn_start_slave():
    slave_app = get_app('slave_adelphos', None, adelphos_slave_instance)
    uvicorn.run(slave_app, host="127.0.0.1", port=8001, reload=False)



#@pytest.mark.asyncio( loop_scope = "session" )
#@pytest.mark.anyio
#@pytest.mark.asyncio
#async def test_ad_2():
#    server_thread = threading.Thread(target = uvicorn_start_slave, daemon = True)
#    server_thread.start()
#    time.sleep(1)


#@pytest.mark.anyio
#async def test_ad_1():
#@pytest.mark.asyncio
@pytest.mark.anyio
async def test_ad_1():

    #server_thread = threading.Thread(target = uvicorn_start_slave, daemon = True)
    #server_thread.start()
    #time.sleep(1)

    client = TestClient(get_app('adelphos_t1', None, adelphos_t1_test))
    with client:

        with client.websocket_connect("/api/ws") as websocket:
            websocket.send_text('login alias ##john.jf password john11')
            data = websocket.receive_text()
            assert re.match('Login OK.*', data) is not None

        with client.websocket_connect("/api/ws") as websocket:
            websocket.send_text('login alias ##john.jf password john12')
            data = websocket.receive_text()
            assert re.match('User error: Invalid username/password', data) is not None

        #time.sleep(1)

        #with client.websocket_connect("/api/ws") as websocket:
        #    websocket.send_text('backdoor alias ##root.admins password supercippo$88')
        #    data = websocket.receive_text()
        #    assert data == 'backdoor OK' 


