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

import re
import tests.t_utils as tu
from app.exc.AdelphosException import AdErrno
from app.logging import gCon


def ws_invite_user_raw(ws, user_handle, invite_code, 
                   code_exp = AdErrno.DONE_OK):

    tu.ws_send_cmd(ws, f"family.invite user_handle {user_handle} \
invite_code {invite_code}", code_exp)


def ws_invite_user_macro(ws, user_handle, invite_code, user_inbox):

    ws_invite_user_raw(ws, user_handle, invite_code)
    count_msg = user_inbox.count_msg()
    assert count_msg == 1

    msg = user_inbox.pop_lst_msg()

    code_mt = re.search("invite_code (.*)$", msg.content)
    assert code_mt is not None

    code_got = code_mt.group(1)
    assert code_got == invite_code

    gCon.log(f"the msg is {msg.content}")


def ws_accept_invite_raw(ws, remote_adelphos, alias_chosen,
                         family, invite_code, password, from_user, user_inbox,
                         code_exp = AdErrno.DONE_OK):

    tu.ws_send_cmd(ws, f"dbg.sndpost to {remote_adelphos} msg \
'alias {alias_chosen} family {family} invite_code {invite_code} password {password}' from {from_user}", code_exp)

    count_msg = user_inbox.count_msg()
    assert count_msg == 1

    msg = user_inbox.pop_lst_msg()
    gCon.log(f"the msg is {msg.content}")


