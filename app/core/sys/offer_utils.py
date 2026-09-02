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

import app.core.sys.object_utils as ou

async def offer_get_adelphos_from(kernel, offer_ob, t_id):
    return await ou.object_get_field_uri_locked(kernel, offer_ob,
             'adelphos_from', t_id)

