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

def _test_remote_add(test1, test2, host2, exp_errno_code = None):

    with test1, test2:
        with test1.websocket_connect(CNST.WS_ROUTE) as websocket:
            websocket.send_text(
    f"dbg.radd host {host2} n1 11 n2 22")

            if exp_errno_code is None:
                data = tu.ws_assert_code(websocket, AdErrno.DONE_OK)
                tu.data_assert_human_output(data, '33')
            else:
                tu.ws_assert_code(websocket, exp_errno_code)

            #data = websocket.receive_text()
            #if exp_errno_code == None:
            #    assert data == "33"
            #else:
            #    assert exp_errno_code == AdelphosBaseException.parse_exc_str(data)


