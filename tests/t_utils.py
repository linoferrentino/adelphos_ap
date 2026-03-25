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


from app.logging import gCon
import time
from fastapi.testclient import TestClient
from app.AdelphosApp import get_app
from app.AdelphosApp import del_app
import json
from app.api.AdelphosException import EAdelhposErrno


# must_wait is true when we have to connect to a remote instance.
def generator_test_client(instance_conf, must_wait):

    if must_wait:
        time.sleep(1.2)
    client = TestClient(get_app(instance_conf['General']['name'], None, 
                                instance_conf))
    with client:
        if must_wait:
            time.sleep(0.5)
        yield client
    del_app()


def websocket_get_next_msg(websocket):
    datas = websocket.receive_text()
    data_parsed = json.loads(datas)
    return data_parsed


def websocket_assert_payload(websocket, payload_expected):
    data = websocket_get_next_msg(websocket)
    assert data['payload'] == payload_expected


def websocket_assert_code(websocket, code_expected):
    data = websocket_get_next_msg(websocket)
    code_got = data['res']
    assert code_got == code_expected


# enforces that all the commands on the script are successful
def play_script_on_instance_OK(adelphos_instance, script):

    with adelphos_instance.websocket_connect("/api/ws") as websocket:
        for line in script:
            websocket.send_text(line)
            websocket_assert_code(websocket, EAdelhposErrno.DONE_OK)


