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
from app.core.ECoreErrno import ECoreErrno
from app.logging import gCon
import tests.social.social_tests as stests


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


def ws_associate_with_family(ws, family_dest, import_export_tax, *, 
            location = None, family_source = None,
            upper_name = None, change_ratio = None,
            brotherhood_ratio = None,
            code_exp = ECoreErrno.DONE_OK):
    cmd = f"family.associate \
import_export_tax {import_export_tax} family_dest {family_dest}"
    if location is not None:
        cmd += f" location '{location}'"
    if family_source is not None:
        cmd += f" family_source {family_source}"
    if upper_name is not None:
        cmd += f" upper_name {upper_name}"
    if change_ratio is not None:
        cmd += f" change_ratio {change_ratio}"
    if brotherhood_ratio is not None:
        cmd += f" brotherhood_ratio {brotherhood_ratio}"
    return tu.ws_send_cmd(ws, cmd, code_exp)


def ws_accept_invite_raw(ws, remote_adelphos, alias_chosen,
                         family, invite_code, password, user_inbox):

    join_msg = f"alias.join_family alias {alias_chosen} family {family} \
invite_code {invite_code} password {password}"

    stests.post_to_daemon_and_check_ws(ws, remote_adelphos,
            join_msg, user_inbox, f'OK, You can join family {family}.')

