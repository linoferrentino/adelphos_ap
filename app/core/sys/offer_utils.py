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
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno
from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType
from app.sdc.Dependencies import Dependencies

import app.core.sys.sys_calls_utils as scu
from app.logging import gCon

import app.core.sys.family_utils as fu
import app.core.sys.alias_utils as autils
import app.misc.trust_utils as tutils
import app.core.sys.ecommerce_utils as ecut
import app.core.sys.agora_utils as au


async def offer_get_adelphos_from(kernel, offer_ob, t_id):
    return await ou.object_get_field_uri_locked(kernel, offer_ob,
             'adelphos_from', t_id)


async def is_offer_exported(kernel, offer_ob, exp_chain, t_id):
    gCon.log(f"is_offer_exported {offer_ob().uri.unparse()}")
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    current_price = await offer_ob().get_scalar('price', t_id)
    for family in exp_chain:
        current_price_db = tutils.abs_to_db(current_price)
        cur_trust = await family().get_scalar('my_trust', t_id)
        if cur_trust < current_price_db:
            gCon.log(f"Cannot export! {cur_trust} < {current_price_db}")
            return (False, current_price)
        cur_tax = await family().get_scalar('import_export_tax', t_id)
        current_price *= cur_tax
    return (True, current_price)


async def is_object_still_available(kernel, object_uri, seller_family, t_id):
    agora_ob = await fu.family_get_your_agora(kernel,
                    seller_family, t_id)
    return await agora_ob().is_in_set('offers', object_uri, t_id)


async def offer_buy_impl(kernel, object_uri, buyer_uri, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    offer_ob = await fdb.uri_read_str(t_id, object_uri, must_lock = True)
    buyer_ob = await fdb.uri_read_str(t_id, buyer_uri,
                                      must_lock = True)
    buyer_family = await autils.alias_ob_get_your_family(kernel,
            buyer_ob, t_id)
    seller_ob = await offer_get_adelphos_from(kernel, offer_ob, t_id)
    seller_family = await autils.alias_ob_get_your_family(kernel,
                seller_ob, t_id)

    avail = await is_object_still_available(kernel, object_uri,
                                seller_family, t_id)
    if avail == False:
        raise AdelphosCoreException(ECoreErrno.EOBJECT_UNAVAILABLE,
                    f"Object {object_uri} not available any more")

    gCon.log(f"you want to buy as {buyer_uri} object {object_uri}")
    (exp_chain, imp_chain) = await get_export_import_chains(kernel,
                seller_family, buyer_family, t_id)
    gCon.log(f"export chain {exp_chain}")
    gCon.log(f"import chain {imp_chain}")

    if len(exp_chain) == 1:
        raise AdelphosCoreException(ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY,
             f"The object '{await offer_ob().get_scalar('title', t_id)}' is originated by your family.")

    (res, agora_exported_price) =  await is_offer_exported(kernel,
                offer_ob, exp_chain, t_id)
    if res == False:
        raise AdelphosCoreException(ECoreErrno.EOBJECT_NOT_EXPORTED,
                                    f"{object_uri} not exported")

    #global_export_tax = await ecut.get_total_tax_up(exp_chain, t_id)
    #gCon.log(f"The export tax total is {global_export_tax}")

    price = await offer_ob().get_scalar('price', t_id)
    #agora_exported_price = price * global_export_tax
    gCon.log(f"The price is {price} in agora is {agora_exported_price}")

    await ecut.distribuite_losses_to_imports(kernel, agora_exported_price,
                                       imp_chain, t_id)

    await ecut.distribuite_gains_to_exports(kernel, agora_exported_price,
                                      exp_chain, t_id)

    await au.remove_object_from_agora(kernel, seller_family, offer_ob, t_id)

    return (exp_chain, imp_chain)


async def get_export_import_chains(kernel, seller_family, buyer_family, t_id):
    exp_chain = list()
    imp_chain = list()
    exp_chain.append(seller_family)
    imp_chain.append(buyer_family)
    exp_cursor = seller_family().uri.unparse()
    imp_cursor = buyer_family().uri.unparse()
    while exp_cursor != imp_cursor:
        gCon.log(f"{exp_cursor} != {imp_cursor} going up!")
        (seller_family, exp_cursor) = await _make_upper_step(
            kernel, seller_family, exp_chain, t_id)

        (buyer_family, imp_cursor) = await _make_upper_step(
            kernel, buyer_family, imp_chain, t_id)
    gCon.log(f"Found the common family {exp_cursor}")
    return (exp_chain, imp_chain)


async def _make_upper_step(kernel, family, chain, t_id):
    upper_family = await fu.family_get_upper_family(kernel,
                    family, t_id, maybe = True)
    if upper_family is None:
        raise AdelphosCoreException(ECoreErrno.EINVALID_CHAIN,
          f"Cannot buy, there is not a common agora.")
    upper_cursor = upper_family().uri.unparse()
    chain.append(upper_family)
    return (upper_family, upper_cursor)


async def object_put_ad_in_agora_impl(kernel, family_ob, alias_ob,
                                       pars ,t_id):
    gCon.log(f"Adding object in family's agora {family_ob().ob.fields}")
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    agora_ob = await fu.family_get_your_agora(kernel,
                        family_ob, t_id)

    object_id = await agora_ob().get_scalar('next_object_id', t_id)
    agora_ob().set_scalar('next_object_id', object_id + 1)

    object_ob = _create_object_from_pars(kernel, family_ob,
                object_id, pars, t_id)
    gCon.log(f"Created the object {object_ob().ob.fields}")

    object_ob().set_link('adelphos_from', alias_ob)

    agora_ob().add_link('offers', object_ob)

    #await _export_object_in_upper_agorai(kernel,
    #            family_ob, pars['price'], object_ob, t_id)

    ob_uri = object_ob().uri.unparse()

    return {
      'msg' : f"Created the ad, the object has its uri {ob_uri}",
      'ob_uri' : ob_uri
    }


#async def _export_object_in_upper_agorai(kernel, family_ob, cur_price,
#                        object_ob, t_id):
#    upper_family_ob = await fu.family_get_upper_family(kernel,
#                    family_ob, t_id, maybe = True)
#
#    if upper_family_ob is None:
#        return
#
#    export_trust = await family_ob().get_scalar('my_trust', t_id)
#    tax = await family_ob().get_scalar('import_export_tax', t_id)
#
#    new_price = tax * cur_price
#    new_price_db = tutils.abs_to_db(new_price)
#    if new_price_db > export_trust:
#        return
#
#    agora_upper = await fu.family_get_your_agora(kernel,
#                        upper_family_ob, t_id)
#    agora_upper().add_link('offers', object_ob)
#
#    await _export_object_in_upper_agorai(kernel,
#            upper_family_ob, new_price, object_ob, t_id)
#

def _create_object_from_pars(kernel, family_ob, object_id, pars, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    ob_name = f"{object_id}_" + family_ob().uri.name
    gCon.log(f"Create an object with name {ob_name}")
    ob_uri = AdelphosUri.create_uri(EAdelphosType.OBJECT_TYPE, ob_name)

    object_ob = fdb.new_ob_uri(t_id, ob_uri, fields = {
        'price' : pars['price'],
        'title' : pars['title'],
        'description' : pars['description'],
        })

    return object_ob


