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


def ws_list_ads(ws, uplevel, *, code_exp = ECoreErrno.DONE_OK):
    cmd = f"agora.list_ads uplevel {uplevel}"
    return tu.ws_send_cmd(ws, cmd, code_exp)


def ws_buy_object_uri(ws, ob_uri, *,
                        code_exp = ECoreErrno.DONE_OK):
    cmd = f"agora.buy_object_uri ob_uri {ob_uri}"
    return tu.ws_send_cmd(ws, cmd, code_exp)


def ws_give_hearts(ws, hearts, task_uri, *, code_exp = ECoreErrno.DONE_OK):
    cmd = f"agora.give_hearts hearts {hearts} task_uri {task_uri}"
    return tu.ws_send_cmd(ws, cmd, code_exp)


