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

from app.api.UserSession import active_login
from app.core.algo.utils import federated_transaction
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno
from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType
from app.sdc.Dependencies import Dependencies

import app.core.sys.sys_calls_utils as scu
from app.logging import gCon

import app.core.sys.family_utils as fu
import app.misc.trust_utils as tutils


class ObjectCalls:


    @staticmethod
    @active_login
    async def _sys_call_put_ad(kernel, session, pars):
        pars['_session'] = session
        return await ObjectCalls._object_put_add_in_agora_safe(kernel, pars)
 

    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def _object_put_add_in_agora_safe(kernel, pars ,t_id):
        family_ob = await scu.get_family_in_session(kernel, pars, t_id)
        gCon.log(f"Adding object in family's agora {family_ob().ob.fields}")
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

        agora_ob = await fu.family_get_your_agora(kernel,
                            family_ob, t_id)

        object_id = agora_ob().get_scalar('next_object_id')
        agora_ob().set_scalar('next_object_id', object_id + 1)

        object_ob = ObjectCalls._create_object_from_pars(kernel, family_ob,
                    object_id, pars, t_id)
        gCon.log(f"Created the object {object_ob().ob.fields}")

        alias_ob = await scu.get_alias_in_session(kernel, pars, t_id)

        object_ob().set_link('adelphos_from', alias_ob)

        agora_ob().add_link('offers', object_ob)

        await ObjectCalls._export_object_in_upper_agorai(kernel,
                    family_ob, pars['price'], object_ob, t_id)

        ob_uri = object_ob().uri.unparse()

        return {
          'msg' : f"Created the ad, the object has its uri {ob_uri}",
          'ob_uri' : ob_uri
        }


    @staticmethod
    async def _export_object_in_upper_agorai(kernel, family_ob, cur_price,
                            object_ob, t_id):
        upper_family_ob = await fu.family_get_upper_family(kernel,
                        family_ob, t_id, maybe = True)

        if upper_family_ob is None:
            return

        export_trust = family_ob().get_scalar('my_trust')
        tax = family_ob().get_scalar('import_export_tax')

        new_price = tax * cur_price
        new_price_db = tutils.abs_to_db(new_price)
        if new_price_db > export_trust:
            return

        agora_upper = await fu.family_get_your_agora(kernel,
                            upper_family_ob, t_id)
        agora_upper().add_link('offers', object_ob)

        await ObjectCalls._export_object_in_upper_agorai(kernel,
                upper_family_ob, new_price, object_ob, t_id)


    @staticmethod
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


