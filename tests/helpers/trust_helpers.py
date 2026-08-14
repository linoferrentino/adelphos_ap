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


def ws_create_trust_line(ws, family_to, trust, change_ratio = 1.0):

    tu.ws_send_cmd(ws, f"trustline.create family_to {family_to} trust {trust} \
change_ratio {change_ratio}")
