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

        await ObjectCalls._check_equity(fdb, family_ob, pars['price'], t_id)
        object_ob = ObjectCalls._create_object_from_pars(kernel, family_ob,
                                                         pars, t_id)
        gCon.log(f"Created the object {object_ob().ob.fields}")

        object_ob().set_link('family_src', family_ob)

        agora_uri_str = family_ob().get_scalar('agora')
        agora_ob = await fdb.uri_read_str(t_id, agora_uri_str, must_lock = True,
                                only_local = True)
        agora_ob().add_link('offers', object_ob)

        ob_uri = object_ob().uri.unparse()

        return {
          'msg' : f"Created the ad, the object has its uri {ob_uri}",
          'ob_uri' : ob_uri
        }


    @staticmethod
    async def _check_equity(fdb, family_ob, price, t_id):
        fam_equity = family_ob().get_scalar('equity')
        if price < (2 * fam_equity):
            return

        upper_family = family_ob().get_scalar('upper_family')
        if upper_family is None:
            raise AdelphosCoreException(ECoreErrno.EEQUITY_OVERFLOW, f"""
Price of object {price} is greater than
two times your family's equity {fam_equity}, and no upper level is possible.
Lower the price or increase your family's equity
(if you are the boss), or consider joining other families in a larger group.""")

        family_ob = await fdb.uri_read_str(t_id, upper_family,
                                           must_lock = True)
        return await _check_equity(fdb, family_ob, price, t_id)


    @staticmethod
    def _create_object_from_pars(kernel, family_ob, pars, t_id):
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        ob_name = "".join(pars['description'].split())
        ob_name = re.sub(r"\W", "_", ob_name)
        ob_name += "_" + family_ob().uri.name
        gCon.log(f"Create an object with name {ob_name}")
        ob_uri = AdelphosUri.create_uri(EAdelphosType.OBJECT_TYPE, ob_name)

        object_ob = fdb.new_ob_uri(t_id, ob_uri, fields = {
            'price' : pars['price'],
            'description' : pars['description']
            })

        return object_ob


