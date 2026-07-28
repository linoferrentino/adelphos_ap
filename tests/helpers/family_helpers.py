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

import tests.t_utils as tu
from app.exc.AdelphosException import AdErrno

def ws_invite_user(ws, user_handle, invite_code, code_exp = AdErrno.DONE_OK):

    tu.ws_send_cmd(ws, f"family.invite user_handle {user_handle} \
invite_code {invite_code}", code_exp)

