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
from app.exc.AdelphosException import parse_exc_str
from app.exc.AdelphosException import AdErrno
from app.sdc.Dependencies import Dependencies

def _test_remote_add(test1, test2, host2):

    with test1, test2:
        with test1.websocket_connect(CNST.WS_ROUTE) as websocket:
            websocket.send_text(
    f"dbg.radd host @{host2} n1 11 n2 22")
            data = websocket.receive_text()
            assert data == "33"

