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
from app.sdc.Dependencies import Dependencies
from app.exc.AdelphosException import AdErrno



def ws_alias_login_in_app(wrapper, social_user, ws, alias, password):
    user_inbox = wrapper.app.routable.get_dep(
                Dependencies.SOCIAL).login_user(social_user)
    user_inbox.clear()
    ws_alias_login(user_inbox, ws, alias, password)


def ws_create_user_alias(ws, user, alias, password):
    ws.send_text(f"root.add_user user {user} alias {alias} password {password}")
    tu.ws_assert_code(ws, AdErrno.DONE_OK)


def ws_alias_logout(ws):
    ws.send_text(f"alias.logout")
    tu.ws_assert_code(ws, AdErrno.DONE_OK)
    ws.send_text(f"alias.whoami")
    tu.ws_assert_code(ws, AdErrno.ENOLOGIN)


def ws_sudo_push_alias(ws, alias):
    ws.send_text(f"root.push_alias alias {alias}")
    tu.ws_assert_code(ws, AdErrno.DONE_OK)
    ws.send_text(f"alias.whoami")
    data = tu.ws_assert_code(ws, AdErrno.DONE_OK)
    tu.data_assert_key_value(data, 'active_login', alias)


def ws_pop_alias(ws):
    ws.send_text(f"root.pop_alias")
    tu.ws_assert_code(ws, AdErrno.DONE_OK)
    ws.send_text(f"alias.whoami")
    data = tu.ws_assert_code(ws, AdErrno.DONE_OK)
    tu.data_assert_key_value(data, 'active_login', 'root.admins')


def ws_alias_login(user_inbox, ws, alias, password):

    ws.send_text(f"alias.login login {alias} password {password}")
    tu.ws_assert_code(ws, AdErrno.DONE_OK)

    count_msg = user_inbox.count_msg()
    assert count_msg == 1

    msg = user_inbox.pop_lst_msg()
    match_tk = re.match('Copy this command to finalize', msg.content)
    assert match_tk is not None

    token_tk = re.search(r"tk (.*)$", msg.content)
    assert token_tk is not None
    token = token_tk.group(1)
    token = token[:-1]

    ws.send_text(f"alias.put_token tk {token}")
    tu.ws_assert_code(ws, AdErrno.DONE_OK)

    ws.send_text(f"alias.whoami")
    data = tu.ws_assert_code(ws, AdErrno.DONE_OK)
    tu.data_assert_key_value(data, 'active_login', alias)

