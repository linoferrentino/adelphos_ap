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

    await object_ob().set_link('adelphos_from', alias_ob, t_id)

    agora_ob().add_link('offers', object_ob)

    ob_uri = object_ob().uri.unparse()

    return {
      'msg' : f"Created the ad, the object has its uri {ob_uri}",
      'ob_uri' : ob_uri
    }


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


