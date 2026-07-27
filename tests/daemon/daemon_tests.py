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

import app.consts as CNST
#from app.exc.AdelphosException import parse_exc_str
from app.exc.AdelphosException import AdErrno
from app.core.AdelphosCoreException import AdelphosBaseException
from app.sdc.Dependencies import Dependencies
import tests.t_utils as tu
from app.logging import gCon


def ws_authorize_remote_adelphos(ws, host, exp_errno_code = None):
    ws.send_text(f"root.allow_remote host {host}")
    tu.ws_assert_code(ws, AdErrno.DONE_OK)


def ws_deny_remote_adelphos(ws, host, exp_errno_code = None):
    ws.send_text(f"root.deny_remote host {host}")
    tu.ws_assert_code(ws, AdErrno.DONE_OK)


def _test_remote_add(test1, test2, host2, exp_errno_code = None):

    with test1, test2:
        with test1.websocket_connect(CNST.WS_ROUTE) as websocket:
            ws_test_remote_add(websocket, host2, exp_errno_code)


def ws_test_remote_add(ws, host2, exp_errno_code = None):

    ws.send_text(f"dbg.radd host {host2} n1 19 n2 22")

    if exp_errno_code is None:
        data = tu.ws_assert_code(ws, AdErrno.DONE_OK)
        gCon.log(f"========================== data is {data}")
        tu.data_assert_res_str(data, '41')
    else:
        tu.ws_assert_code(ws, exp_errno_code)


