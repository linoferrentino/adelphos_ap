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

from app.core.ECoreErrno import ECoreErrno
import tests.t_utils as tu


def ws_object_change_price(ws, ob_uri, new_price, *,
    exp_errno_code = ECoreErrno.DONE_OK):
    cmd = f"object.change_price ob_uri {ob_uri} new_price {new_price}"
    return tu.ws_send_cmd(ws, cmd, exp_errno_code)


def ws_create_object_ad(ws, title, price, *,
    description = None,
    exp_errno_code = ECoreErrno.DONE_OK):

    cmd = f"object.put_ad title '{title}' price {price}"
    if description is not None:
        cmd += f" description '{description}'"

    ws.send_text(cmd)
    data = tu.ws_assert_code(ws, exp_errno_code)
    return data


