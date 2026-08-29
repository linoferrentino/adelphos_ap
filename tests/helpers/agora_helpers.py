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
from app.logging import gCon


def ws_list_ads(ws, uplevel, *, code_exp = ECoreErrno.DONE_OK,
                only_uri = True):
    cmd = f"agora.list_ads uplevel {uplevel} get_only_uri {only_uri}"
    return tu.ws_send_cmd(ws, cmd, code_exp)


def ws_buy_object(ws, uplevel, index_ad, code_exp = ECoreErrno.DONE_OK):
    cmd = f"agora.buy_object uplevel {uplevel} index_ad {index_ad}"
    return tu.ws_send_cmd(ws, cmd, code_exp)

