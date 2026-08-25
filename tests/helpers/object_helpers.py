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


def ws_create_object_ad(ws, description, price,
    exp_errno_code = ECoreErrno.DONE_OK):

    ws.send_text(f"object.put_ad description '{description}' price {price}")
    data = tu.ws_assert_code(ws, exp_errno_code)
    return data


