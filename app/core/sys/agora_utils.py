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


async def _get_object_title(kernel, family_lev_ob, ad_title, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    offers = await family_list_ads(kernel, family_lev_ob, t_id)

    offer = await _get_offer_from_pars_title(fdb, offers,
                            ad_title, t_id)

    offer_ob = await fdb.uri_read_str(t_id, offer['uri'])

    return (offer, offer_ob)


async def _agora_give_hearts_impl(kernel, pars, t_id):
    token = pars['token']
    hearts = pars['hearts']
    alias_ob = scu.get_alias_in_session(kernel, pars, t_id)

    iterate_on_all_diakonos_task()


async def _agora_buy_object_impl(kernel, pars, t_id):

    uplevel = pars['uplevel']
    ad_title = pars['ad_title']

    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    chain_imports = await scu.get_family_chain_up(kernel, pars, t_id)

    if len(chain_imports) < 2:
        raise AdelphosCoreException(ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY,
                    "You cannot buy in your family")

    family_lev_ob = chain_imports[-1] 

    (offer, offer_ob) = await _get_object_title(kernel, family_lev_ob,
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

    myself_ob = await scu.get_alias_in_session(kernel, pars, t_id)
    await offer_ob().set_link('adelphos_to', myself_ob, t_id)

    skip_task = pars.get('_x_skip_task')
    if (skip_task) is None or (skip_task == False):
        await tku.add_routing_task(kernel, offer_ob, chain_exports,
                                   chain_imports, t_id)
        await ecut.distribute_losses_to_imports(kernel,
                agora_exported_price, chain_imports, False, t_id)

        await ecut.distribute_gains_to_exports(kernel,
                agora_exported_price, chain_exports, False, t_id)
    else:
        await ecut.distribute_losses_to_imports(kernel,
                agora_exported_price, chain_imports, True, t_id)

        await ecut.distribute_gains_to_exports(kernel,
                agora_exported_price, chain_exports, True, t_id)

    await au.remove_object_from_agora(kernel, chain_exports[0],
                                      offer_ob, t_id)

    return (chain_exports, chain_imports)



#async def copy_ads_from_lower_agora(kernel, agora_lower, export_trust,
#              tax, agora_upper, t_id):
#    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
#    list_lower = agora_lower().get_as_list('offers')
#
#    for uri_lower in list_lower:
#        ob_list = await fdb.uri_read_str(t_id, uri_lower, must_lock = True)
#        lower_price = await ob_list().get_scalar('price', t_id)
#        upper_price = tax * lower_price
#
#        upper_price_db = tutils.abs_to_db(upper_price)
#        if upper_price_db > export_trust:
#            gCon.log(f"the object {await ob_list().get_scalar('title', t_id)} has a price {upper_price_db} > of export trust {export_trust}, ignored.")
#            continue
#
#        gCon.log(f"Adding lower uri {uri_lower} --> {ob_list().uri}")
#        agora_upper().add_link('offers', ob_list)
#
