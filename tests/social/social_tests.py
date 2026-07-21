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
from app.exc.AdelphosException import AdErrno
from app.core.AdelphosCoreException import AdelphosBaseException
from app.sdc.Dependencies import Dependencies
import tests.t_utils as tu


def send_to_daemon_ctx(test1, test2, host2, msg, user_from):

    with test1.websocket_connect(CNST.WS_ROUTE) as websocket:
            websocket.send_text(
    f"dbg.sndpost to @adelphos@{host2} msg '{msg}' from {user_from}")
            tu.ws_assert_code(websocket, AdErrno.DONE_OK)
            #data = websocket.receive_text()
            #assert data == "DONE!"


def _send_to_daemon(test1, test2, host2, msg, user_from):

    with test1, test2:
        send_to_daemon_ctx(test1, test2, host2, msg, user_from)

 
def _test_sndpost_to_host(test1, test2, host2, userKO, userOK, user_from):

    with test1, test2:
        with test1.websocket_connect(CNST.WS_ROUTE) as websocket:
            websocket.send_text(
    f"dbg.sndpost to @{userKO}@{host2} msg echo_test_x918 from {user_from}")
            #data = websocket.receive_text()
            #assert AdelphosBaseException.parse_exc_str(data) == \
            #        AdErrno.USER_DOES_NOT_EXIST
            tu.ws_assert_code(websocket, AdErrno.USER_DOES_NOT_EXIST)

            websocket.send_text(
    f"dbg.sndpost to @{userOK}@{host2} msg echo_test_x918 from {user_from}")
            #data = websocket.receive_text()
            #assert data == "DONE!"
            data = tu.ws_assert_code(websocket, AdErrno.DONE_OK)
            tu.data_assert_res_str(data, "DONE!")

            #websocket.close()
            
            user_ob = test2.app.routable.get_dep(
                    Dependencies.SOCIAL).login_user(userOK)
            count_msg = user_ob.count_msg()
            assert count_msg == 1

            msg = user_ob.pop_lst_msg()
            assert msg.content == 'echo_test_x918'

            websocket.send_text(
    f"dbg.sndpost to @{userOK}@{host2} msg echo_test_x911 from {user_from}")
            #data = websocket.receive_text()
            #assert data == "DONE!"
            tu.ws_assert_res_str(websocket, 'DONE!')
            
            user_ob = test2.app.routable.get_dep(
                    Dependencies.SOCIAL).login_user(userOK)
            count_msg = user_ob.count_msg()
            assert count_msg == 1

            msg = user_ob.pop_lst_msg()
            assert msg.content == 'echo_test_x911'

            websocket.close()

