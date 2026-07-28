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


from app.logging import gCon
import time
from starlette.testclient import TestClient
import json
import httpx2
from app.core.AdelphosCoreException import AdelphosBaseException


def _parse_data(datas):
    data_parsed = json.loads(datas)
    return data_parsed


def ws_get_next_msg(websocket):
    datas = websocket.receive_text()
    return _parse_data(datas)


async def ws_get_next_msg_async(ws):
    datas = await ws.receive_text()
    return _parse_data(datas)


def _ws_assert_payload(data, payload_expected):
    assert data['payload'] == payload_expected
    return data


def websocket_assert_payload(websocket, payload_expected):
    data = ws_get_next_msg(websocket)
    return _ws_assert_payload(data, payload_expected)


async def  ws_assert_payload_async(ws, payload_expected):
    data = await ws_get_next_msg_async(ws)
    return _ws_assert_payload(data, payload_expected)


def _ws_assert_code(data, code_expected):
    code_got = data['errno']
    assert isinstance(code_got, int)
    assert code_got == int(code_expected)


def ws_assert_code(websocket, code_expected):
    data = ws_get_next_msg(websocket)
    _ws_assert_code(data, code_expected)
    return data


async def ws_assert_code_async(ws, code_expected):
    data = await ws_get_next_msg_async(ws)
    _ws_assert_code(data, code_expected)
    return data


def ws_assert_code(ws, code_expected):
    data = ws_get_next_msg(ws)
    _ws_assert_code(data, code_expected)
    return data


def data_assert_human_output(data, human_output_exp):
    assert data['human_output'] == human_output_exp


def data_assert_res_str(data, res_output_exp):
    assert data['res'] == res_output_exp


def data_assert_key_value(data, key, value_expected):
    assert data['res'][key] == value_expected


async def ws_assert_human_output_async(ws, human_output_exp):
    data = await ws_get_next_msg_async(ws)
    data_assert_human_output(data, human_output_exp)
    return data


async def ws_assert_res_str_async(ws, res_output_exp):
    data = await ws_get_next_msg_async(ws)
    data_assert_res_str(data, res_output_exp)
    return data


def ws_assert_res_str(ws, res_output_exp):
    data = ws_get_next_msg(ws)
    data_assert_res_str(data, res_output_exp)
    return data


def ws_assert_human_output(ws, human_output_exp):
    data = ws_get_next_msg(ws)
    data_assert_human_output(data, human_output_exp)
    return data


def websocket_assert_payload_success(websocket, payload_expected):
    data = websocket_assert_code(websocket, EAdelhposErrno.DONE_OK)
    return _ws_assert_payload(data, payload_expected)


async def play_script_ws_async(ws, script):
    for item in script:
        (question, expected) = item
        #gCon.log(f'-----------------------> send {question}')
        await ws.send_text(question)
        if isinstance(expected, EAdelhposErrno):
            #gCon.log(f"expected code {expected}")
            await ws_assert_code_async(ws, expected)
        elif isinstance(expected, str):
            #gCon.log(f"expected string {expected}")
            await ws_assert_payload_async(ws, expected)
        else:
            await ws_assert_payload_code_async(ws, expected[0], expected[1])


# enforces that all the commands on the script are successful
def play_script_on_instance_OK(adelphos_instance, script):

    with adelphos_instance.websocket_connect("/api/ws") as websocket:
        for line in script:
            websocket.send_text(line)
            websocket_assert_code(websocket, EAdelhposErrno.DONE_OK)


def assert_error_code_in_response(response, error_expt):
    assert response.status_code == 401
    if isinstance(response, httpx2.Response) == True:
        int_code = AdelphosBaseException.parse_exc_str(response._content.decode())
    else:
        int_code = AdelphosBaseException.parse_exc_str(response.body.decode())
    assert int_code == error_expt 



