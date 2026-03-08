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


# I can have several test instances that speak together.

adelphos_t1_test =  {"General": {
    "debug": True, 
    "port": 5099, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost", 
    "root_user": "@lino_ferre@localhost:5000", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$QK8nKJOBQX0jU+S9fwJpLw$0wV4hG/ar/uJSlcDd4IV6bqEBLWz+rFLFBpuGiyaPjM"}, 
            "demo_users":
   [{"name": "john", "alias": "##john.jf", "password": "john11"}, 
    {"name": "mary", "alias": "##mary.mf", "password": "mary11"}]
}

client = TestClient(get_app('adelphos_t1', adelphos_t1_test))

def test_hello():

    assert 3 == 3


def test_app():

    assert 5 == 5


def test_websocket():
    with client.websocket_connect("/api/daemon_cli") as websocket:
        websocket.send_text('login ##john.jf password john11')
        data = websocket.receive_text()
        assert data == 'impossibile' 

