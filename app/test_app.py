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


#from .AdelphosApp import get_app

from fastapi.testclient import TestClient
from app.logging import gCon
from fastapi.websockets import WebSocket
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def a_test_lifespan(app):
    gCon.rule("LIFESPAN START")
    yield
    gCon.rule("LIFESPAN END")


# I create the test adelphos instance, it can communicate to other adelphoi
# in the same instance.
 

app = FastAPI(root_path = '/api', port = 3939, lifespan = a_test_lifespan)

# the test application has some activity pub users already defined.

@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    await websocket.send_json({"msg": "Hello WebSocket"})
    await websocket.close()


client = TestClient(app, client = ('localhost', 3999))
client1 = TestClient(app, client = ('localhost', 7999))


#def test_read_main():
#    with client:
#        response = client.get("/")
#        assert response.status_code == 200
#        gCon.log("Hello!")
#        assert response.json() == {"msg": "Hello World"}


def test_ws():

    # I want to run the tests using some scripts, and then I check that the
    # db is in the desidered state.
    with client:
        with client.websocket_connect("ws://www.adelphos.it/ws") as websocket:
            data = websocket.receive_json()
            assert data == {"msg": "Hello WebSocket"}


#
## I can have several test instances that speak together.
#
#adelphos_t1_test =  {"General": {
#    "debug": True, 
#    "port": 50000, 
#    "db_name": ":memory:", 
#    "private_key": ":memory:", 
#    "host":  "localhost:50000", 
#    "root_user": "@john@localhost:50000", 
#    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$QK8nKJOBQX0jU+S9fwJpLw$0wV4hG/ar/uJSlcDd4IV6bqEBLWz+rFLFBpuGiyaPjM"}, 
#            "demo_users":
#   [{"name": "john", "alias": "##john.jf", "password": "john11"}, 
#    {"name": "mary", "alias": "##mary.mf", "password": "mary11"}]
#}
##
##
#
#client1 = TestClient(get_app('adelphos_t1', adelphos_t1_test))
#
#def test_ad_1():
#
#    with client1:
#        with client1.websocket_connect("/api/ws") as websocket:
#            assert 4 == 4
#


#
#import pytest
#
#@pytest.mark.anyio
#async def test_a1():
#    with client:
#        response = client.get('https://localhost:999/api/users/daemon')
#        assert response.status_code == 200
#        print(response)
##
##
##def test_ws():
##
##    with client.websocket_connect("wss://127.0.0.1:12000/api/ws") as websocket:
##        data = websocket.send('eee')
###
#import time




#def test_websocket():
#
#    with TestClient(get_app('adelphos_t1', adelphos_t1_test)) as client:
#        #with client.websocket_connect("wss://localhost:12000/api/ws") as websocket:
#            #websocket.send('login ##john.jf password john11')
#            #data = websocket.receive_text()
#            #assert data == 'impossibile' 
#        response = client.get('/api/users/daemon')
#        assert response.status_code == 200
#        print(response)
#



#def test_websocket():
#
#    with TestClient(get_app('adelphos_t1', adelphos_t1_test), 
#                    base_url = 'https://localhost:12000/api', 
#                    client = ('localhost', 12000)) as client:
#        #with client.websocket_connect("wss://localhost:12000/api/ws") as websocket:
#            #websocket.send('login ##john.jf password john11')
#            #data = websocket.receive_text()
#            #assert data == 'impossibile' 
#        response = client.get('/api/users/daemon')
#        assert response.status_code == 200
#        print(response)
#

#def test_websocket():
#
#    with TestClient(get_app('adelphos_t1', adelphos_t1_test), client = ('localhost', 12000)) as client:
#            #websocket = client.websocket_connect("wss://localhost:5089/api/daemon_cli")
#            with client.websocket_connect("wss://localhost:12000/api/ws") as websocket:
#            #with client.websocket_connect("/api/daemon_cli") as websocket:
#                websocket.send('login ##john.jf password john11')
#                #data = websocket.receive_text()
#                #assert data == 'impossibile' 
#                assert 4 == 4



#def test_ws():
#    #with TestClient(get_app()) as client:
#    with TestClient(get_app('adelphos_t1', adelphos_t1_test), 
#                    client = ('localhost', 5099)) as client:
#        # Application's lifespan is called on entering the block.
#        assert  4 == 4
#
#        #with client.websocket_connect("wss://localhost:5099/api/daemon_cli") as websocket:
#        #with client.websocket_connect("/api/daemon_cli") as websocket:
#        #    websocket.send_text('login ##john.jf password john11')
#        #    data = websocket.receive_text()
#        #    assert data == 'impossibile' 
#
