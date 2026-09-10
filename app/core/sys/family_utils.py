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


from app.sdc.Dependencies import Dependencies
import app.core.sys.sys_calls_utils as scu
import app.core.sys.agora_utils as au
import app.core.sys.object_utils as ou
import app.core.sys.ecommerce_utils as ecut
from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.AdelphosUri import AdelphosUri
from app.logging import gCon

import app.misc.trust_utils as tutils


async def family_get_offers_deep(fdb, fob, t_id):
    gCon.log(f"[red]get Recursive offers for {fob().uri.unparse()}[/red]")
    agora_ob = await family_get_your_agora(fdb.kernel, fob, t_id) 
    offers_set = await agora_ob().get_set('offers', t_id)

    level = await fob().get_scalar('level', t_id)
    gCon.log(f"lev {level} offers set is {offers_set}")
    if (level == 0):
        return offers_set
    
    members_list = await fob().get_as_object_list('members', t_id)
    gCon.log(f"fam members are {members_list}")

    for member in members_list:
        gCon.log(f"Adding the member {member} type {type(member)}")
        offers_deep = await member().get_as_object_list('offers_deep', t_id)
        exp_trust = await member().get_scalar('my_trust', t_id)

        for offer in offers_deep:
            price_offer = await offer().get_scalar('price', t_id)
            price_offer_db = tutils.abs_to_db(price_offer)
            gCon.log(f"price {price_offer_db} exp_trust {exp_trust}")
            if price_offer_db < exp_trust:
                offers_set.add(offer)
            else:
                title = await offer().get_scalar('title', t_id)
                gCon.log(f"offer {title} cannot be exported.")

    return offers_set


async def family_get_your_boss(kernel, family_ob, t_id):
    return await ou.object_get_field_uri_locked(kernel, family_ob,
                                                'boss', t_id)


async def family_get_your_agora(kernel, family_ob, t_id):
    return await ou.object_get_field_uri_locked(kernel, family_ob,
                                                'agora', t_id)


async def family_get_upper_family(kernel, family_ob, t_id, *,
                                  maybe = False):
    return await ou.object_get_field_uri_locked(kernel, family_ob,
                     'upper_family', t_id, maybe = maybe)


async def family_get_chain_alias_family_to(kernel,
            alias_ob, family_ob, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)


async def family_associate_2nd_half(kernel, pars, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    gCon.log(f"family associate 2nd half {pars}")

    family_src_ob = await scu.get_family_source(kernel, pars, t_id)
    family_dst_ob = await scu.get_family_dest(kernel, pars, t_id)

    boss_ob = await family_get_your_boss(kernel, family_src_ob, t_id)

    gCon.log(f"family src {family_src_ob().ob.fields} dst {family_dst_ob().ob.fields}")

    new_level = await family_src_ob().get_scalar('level', t_id) + 1

    upper_family_name = pars['upper_name']
    gCon.log(f"upper_family_name |{upper_family_name}|")

    family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE, upper_family_name)

    trust_in_src = await family_src_ob().get_scalar('my_trust', t_id)
    trust_in_dst = await family_dst_ob().get_scalar('my_trust', t_id)
    trust_in_tot = max(trust_in_src, trust_in_dst)
    gCon.log(f"trust in1 {trust_in_src} trust_in_dst {trust_in_dst}")

    family_ob = fdb.new_ob_uri(t_id, family_uri, fields = {
        'level' : new_level,
        'brotherhood_ratio': pars['brotherhood_ratio'],
        'my_trust' : trust_in_tot,
        })

    family_ob().set_link('boss', boss_ob)
    family_ob().add_link('members', family_src_ob)
    family_ob().add_link('members', family_dst_ob)

    agora_ob = add_default_agora(fdb, family_ob, boss_ob, pars['location'],
                                 t_id)
    family_src_ob().set_link('upper_family', family_ob)
    family_dst_ob().set_link('upper_family', family_ob)

    #agora_src = await family_get_your_agora(kernel, family_src_ob, t_id)
    #agora_dst = await family_get_your_agora(kernel, family_dst_ob, t_id)

    #tax_src = await ecut.get_total_tax_chain_str(kernel,
    #            pars['family_src_chain'], t_id)
    #export_trust = await family_src_ob().get_scalar('my_trust', t_id)

    #await au.copy_ads_from_lower_agora(kernel, agora_src, export_trust,
    #                                   tax_src, agora_ob, t_id)

    #tax_dst = await ecut.get_total_tax_chain_str(kernel,
    #            pars['family_dst_chain'], t_id)
    #export_trust = await family_dst_ob().get_scalar('my_trust', t_id)
    #await au.copy_ads_from_lower_agora(kernel, agora_dst, export_trust,
    #                                   tax_dst, agora_ob, t_id)


def add_default_agora(fdb, family_ob, alias_ob, location, t_id):
    agora_name = family_ob().uri.name + "_main_agora"

    fields = {
       'location': location
    }
    agora_ob = fdb.new_ob(t_id, EAdelphosType.AGORA_TYPE,
                    agora_name, fields = fields)
    agora_ob().set_link('carrier', alias_ob)
    family_ob().set_link('agora', agora_ob)

    return agora_ob


