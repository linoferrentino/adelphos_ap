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


async def copy_ads_from_lower_agora(kernel, agora_lower, tax,
                                    agora_upper, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    list_lower = agora_lower().get_as_list('offers')

    for uri_lower in list_lower:
        ob_list = await fdb.uri_read_str(t_id, uri_lower, must_lock = True)
        lower_price = ob_list().get_as_list('price')[-1]
        upper_price = tax * lower_price
        ob_list().add_scalar('price', upper_price)
        gCon.log(f"Adding lower uri {uri_lower} --> {ob_list().uri}")
        agora_upper().add_link('offers', ob_list)

