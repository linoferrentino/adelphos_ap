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

def _test_sndpost_to_host(test1, test2, host2, userKO, userOK, user_from):

    with test1, test2:
        with test1.websocket_connect(CNST.WS_ROUTE) as websocket:
            websocket.send_text(
    f"dbg.sndpost to @{userKO}@{host2} msg echo_test_x918 from {user_from}")
            data = websocket.receive_text()
            assert parse_exc_str(data) == AdErrno.USER_DOES_NOT_EXIST

            websocket.send_text(
    f"dbg.sndpost to @{userOK}@{host2} msg echo_test_x918 from {user_from}")
            data = websocket.receive_text()
            assert data == "DONE!"

            websocket.close()
            
            user_ob = test2.app.routable.get_dep(
                    Dependencies.SOCIAL).login_user(userOK)
            count_msg = user_ob.count_msg()
            assert count_msg == 1

            msg = user_ob.pop_lst_msg()
            assert msg == 'echo_test_x918'


