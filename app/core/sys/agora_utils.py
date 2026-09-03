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

from app.logging import gCon
from app.sdc.Dependencies import Dependencies

import app.misc.trust_utils as tutils 
import app.core.sys.family_utils as fu
import app.core.sys.object_utils as ou


async def agora_get_your_carrier(kernel, family_ob, t_id):
    return await ou.object_get_field_uri_locked(kernel, family_ob,
                                                'carrier', t_id)


async def remove_object_from_export_chain(kernel, chain_exports, offer_ob,
                                          t_id):
    for family in chain_exports:
        agora_family = await fu.family_get_your_agora(kernel, family,
                                                      t_id)
        agora_family().remove_link('offers', offer_ob)


async def copy_ads_from_lower_agora(kernel, agora_lower, export_trust,
              tax, agora_upper, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    list_lower = agora_lower().get_as_list('offers')

    for uri_lower in list_lower:
        ob_list = await fdb.uri_read_str(t_id, uri_lower, must_lock = True)
        lower_price = ob_list().get_scalar('price')
        upper_price = tax * lower_price

        upper_price_db = tutils.abs_to_db(upper_price)
        if upper_price_db > export_trust:
            gCon.log(f"the object {ob_list().get_scalar('title')} has a price {upper_price_db} > of export trust {export_trust}, ignored.")
            continue

        gCon.log(f"Adding lower uri {uri_lower} --> {ob_list().uri}")
        agora_upper().add_link('offers', ob_list)

