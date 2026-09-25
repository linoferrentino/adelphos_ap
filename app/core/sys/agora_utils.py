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

import re

from app.logging import gCon
from app.sdc.Dependencies import Dependencies

import app.misc.trust_utils as tutils 
import app.core.sys.agora_utils as au
import app.core.sys.ecommerce_utils as ecut
import app.core.sys.family_utils as fu
import app.core.sys.object_utils as ou
import app.core.sys.sys_calls_utils as scu
import app.core.sys.alias_utils as alu
import app.core.sys.task_utils as tku
from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException


async def agora_get_your_carrier(kernel, family_ob, t_id):
    return await ou.object_get_field_uri_locked(kernel, family_ob,
                                                'carrier', t_id)


async def remove_object_from_agora(kernel, seller_family, offer_ob, t_id):
    agora_family = await fu.family_get_your_agora(kernel, seller_family, t_id)
    await agora_family().remove_link('offers', offer_ob, t_id)


async def family_list_ads(kernel, family_lev_ob, t_id):

    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    offers = await family_lev_ob().get_as_list('offers_deep', t_id)
    return offers


async def _get_offer_from_pars_title(fdb, offers, par_title, t_id):
    for offer in offers:
        gCon.log(f"Processing offer {offer}")
        if re.search(par_title, offer['title']) is not None:
            gCon.log(f"found!")
            return offer
    raise AdelphosCoreException(ECoreErrno.ENO_SUCH_OBJECT,
                f"no object with title {par_title} found")


async def _get_first_object_title(kernel, family_lev_ob, ad_title, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    offers = await family_list_ads(kernel, family_lev_ob, t_id)

    offer = await _get_offer_from_pars_title(fdb, offers,
                            ad_title, t_id)

    offer_ob = await fdb.uri_read_str(t_id, offer['uri'])

    return (offer, offer_ob)


async def agora_find_first_object_title_impl(kernel, pars, t_id):
    uplevel = pars['uplevel']
    ob_title = pars['ob_title']

    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    chain_imports = await scu.get_family_chain_up(kernel, pars, t_id)

    if len(chain_imports) < 2:
        raise AdelphosCoreException(ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY,
                    "You cannot buy in your family")

    family_lev_ob = chain_imports[-1] 

    (offer, offer_ob) = await _get_first_object_title(kernel, family_lev_ob,
                                                ob_title, t_id)

    return (offer,)


async def _agora_buy_object_uri_impl(kernel, pars, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    ob_uri = pars['ob_uri']
    offer_ob = await fdb.uri_read_str(t_id, ob_uri)
    alias_uri_str = await offer_ob().get_scalar('adelphos_from', t_id)
    family_from_ob = await alu.alias_get_your_family(
            kernel, alias_uri_str, t_id)
    family_from_src = family_from_ob().uri.unparse()

    my_family = await scu.get_family_in_session(kernel, pars, t_id)

    (chain_exports, chain_imports) = await scu.find_first_common_parent(
            kernel, family_from_ob, my_family, t_id)

    if len(chain_imports) < 2:
        raise AdelphosCoreException(ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY,
                    "You cannot buy in your family")

    if family_from_src == chain_imports[0]().uri.unparse():
        raise AdelphosCoreException(ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY,
                   f"The object {await offer_ob().get_scalar('description', t_id)} is originated by your family.")

    myself_ob = await scu.get_alias_in_session(kernel, pars, t_id)
    await offer_ob().set_link('adelphos_to', myself_ob, t_id)

    total_tax = await ecut.get_total_tax_up(chain_exports, t_id)
    offer_price = await offer_ob().get_scalar('price', t_id)
    agora_exported_price = total_tax * offer_price

    skip_task = pars.get('_x_skip_task')
    gCon.log(f"_x_skip_task is {skip_task}")
    if (skip_task is None) or (skip_task == False):
         pending_moves = await ecut.distribute_losses_and_gains(kernel,
                agora_exported_price, chain_exports, chain_imports,
                ecut.EBMod.PENDING, t_id)
         await tku.add_routing_task(kernel, offer_ob, agora_exported_price,
                chain_exports, chain_imports, pending_moves, t_id)
    else:
        await ecut.distribute_losses_and_gains(kernel, agora_exported_price,
                chain_exports, chain_imports, ecut.EBMod.REAL, t_id)

    await au.remove_object_from_agora(kernel, chain_exports[0],
                                      offer_ob, t_id)
    return (chain_exports, chain_imports)



async def _agora_buy_object_impl(kernel, pars, t_id):

    uplevel = pars['uplevel']
    ad_title = pars['ad_title']

    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    chain_imports = await scu.get_family_chain_up(kernel, pars, t_id)

    if len(chain_imports) < 2:
        raise AdelphosCoreException(ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY,
                    "You cannot buy in your family")

    family_lev_ob = chain_imports[-1] 

    (offer, offer_ob) = await _get_first_object_title(kernel, family_lev_ob,
                                                ad_title, t_id)

    offer_uri = offer['uri']
    agora_exported_price = offer['price']
    gCon.log(f"The offer {offer_uri} has a price {agora_exported_price}")

    alias_uri_str = await offer_ob().get_scalar('adelphos_from', t_id)
    family_from_ob = await alu.alias_get_your_family(
            kernel, alias_uri_str, t_id)
    family_from_src = family_from_ob().uri.unparse()

    if family_from_src == chain_imports[0]().uri.unparse():
        raise AdelphosCoreException(ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY,
                   f"The object {await offer_ob().get_scalar('description', t_id)} is originated by your family.")

    chain_exports = await scu.get_family_chain_up_from_to(kernel,
                family_from_src, family_lev_ob, t_id)
    if len(chain_exports) != len(chain_imports):
        raise Exception("This version of adelphos handles symmetric chains: internal error")

    top_export_family_uri = chain_exports[-1]().uri.unparse()
    top_import_family_uri = chain_imports[-1]().uri.unparse()

    assert top_export_family_uri == top_import_family_uri

    semi_top_export_family_uri = chain_exports[-2]().uri.unparse()
    semi_top_import_family_uri = chain_imports[-2]().uri.unparse()

    if semi_top_export_family_uri == semi_top_import_family_uri:
        raise AdelphosCoreException(ECoreErrno.EUPLEVEL_OVERFLOW,
            f"The object {offer_uri} is available in lower agora \
{semi_top_import_family_uri}")

    myself_ob = await scu.get_alias_in_session(kernel, pars, t_id)
    await offer_ob().set_link('adelphos_to', myself_ob, t_id)

    skip_task = pars.get('_x_skip_task')
    gCon.log(f"_x_skip_task is {skip_task}")
    if (skip_task is None) or (skip_task == False):
         pending_moves = await ecut.distribute_losses_and_gains(kernel, agora_exported_price,
                chain_exports, chain_imports, ecut.EBMod.PENDING, t_id)
         await tku.add_routing_task(kernel, offer_ob, agora_exported_price,
                   chain_exports, chain_imports, pending_moves, t_id)
    else:
        await ecut.distribute_losses_and_gains(kernel, agora_exported_price,
                chain_exports, chain_imports, ecut.EBMod.REAL, t_id)

    await au.remove_object_from_agora(kernel, chain_exports[0],
                                      offer_ob, t_id)
    return (chain_exports, chain_imports)


