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
from app.core.ECoreErrno import ECoreErrno


def ws_list_ads(ws, uplevel, *, code_exp = ECoreErrno.DONE_OK):
    cmd = f"agora.list_ads uplevel {uplevel}"
    return tu.ws_send_cmd(ws, cmd, code_exp)

