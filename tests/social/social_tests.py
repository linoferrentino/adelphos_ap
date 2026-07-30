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


def post_to_daemon_and_check(wrap, remote_host, msg, user_inbox,
                             exp_ans, exp_detail = None):
    with wrap.websocket_connect(CNST.WS_ROUTE) as ws:
        count_msg = user_inbox.count_msg()
        user_from = user_inbox.actor_dto.act.preferred_username
        assert count_msg == 0
        ws.send_text(
    f"dbg.sndpost to @adelphos@{remote_host} msg '{msg}' from {user_from}")
        tu.ws_assert_code(ws, AdErrno.DONE_OK)
        count_msg = user_inbox.count_msg()
        assert count_msg == 1
        msg = user_inbox.pop_lst_msg()

        if isinstance(exp_ans, str):
            assert msg.content == exp_ans
        else:
            assert exp_ans == \
                AdelphosBaseException.parse_exc_str(msg.content)
            if exp_detail is None:
                return
            assert exp_detail == \
                AdelphosBaseException.parse_detail(msg.content)


def send_to_daemon_ctx(test1, test2, host2, msg, user_from):

    with test1.websocket_connect(CNST.WS_ROUTE) as websocket:
            websocket.send_text(
    f"dbg.sndpost to @adelphos@{host2} msg '{msg}' from {user_from}")
            tu.ws_assert_code(websocket, AdErrno.DONE_OK)


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

