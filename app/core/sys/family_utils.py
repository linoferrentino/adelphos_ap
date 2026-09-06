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

    family_src_ob = await scu.get_family_source(kernel, pars, t_id)
    family_dst_ob = await scu.get_family_dest(kernel, pars, t_id)

    boss_ob = await family_get_your_boss(kernel, family_src_ob, t_id)

    gCon.log(f"family src {family_src_ob().ob.fields} dst {family_dst_ob().ob.fields}")

    new_level = family_src_ob().get_scalar('level') + 1

    upper_family_name = pars['upper_name']

    family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE, upper_family_name)

    family_ob = fdb.new_ob_uri(t_id, family_uri, fields = {
        'level' : new_level,
        'brotherhood_ratio': pars['brotherhood_ratio']
        })

    family_ob().set_link('boss', boss_ob)
    family_ob().add_link('members', family_src_ob)
    family_ob().add_link('members', family_dst_ob)

    agora_ob = add_default_agora(fdb, family_ob, boss_ob, t_id, location = 
                      pars['location'])
    family_src_ob().set_link('upper_family', family_ob)
    family_dst_ob().set_link('upper_family', family_ob)

    agora_src = await family_get_your_agora(kernel, family_src_ob, t_id)
    agora_dst = await family_get_your_agora(kernel, family_dst_ob, t_id)

    tax_src = await ecut.get_total_tax_chain_str(kernel,
                pars['family_src_chain'], t_id)
    export_trust = family_src_ob().get_scalar('my_trust')

    await au.copy_ads_from_lower_agora(kernel, agora_src, export_trust,
                                       tax_src, agora_ob, t_id)

    tax_dst = await ecut.get_total_tax_chain_str(kernel,
                pars['family_dst_chain'], t_id)
    export_trust = family_dst_ob().get_scalar('my_trust')
    await au.copy_ads_from_lower_agora(kernel, agora_dst, export_trust,
                                       tax_dst, agora_ob, t_id)


def add_default_agora(fdb, family_ob, alias_ob, t_id, *, location = None):
    agora_name = family_ob().uri.name + "_main_agora"

    fields = {}
    if location is not None:
        fields['location'] = location
    agora_ob = fdb.new_ob(t_id, EAdelphosType.AGORA_TYPE,
                    agora_name, fields = fields)
    #agora_ob().set_link('family', family_ob)
    agora_ob().set_link('carrier', alias_ob)
    family_ob().set_link('agora', agora_ob)

    return agora_ob


