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


def ws_create_trust_line(ws, family_to, max_equity):

    tu.ws_send_cmd(ws, f"trustline.create family_to {family_to} max_equity {max_equity}")
