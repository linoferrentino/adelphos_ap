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

from app.core.algo.utils import federated_transaction
from app.logging import gCon
from app.api.UserSession import active_login
from app.sdc.Dependencies import Dependencies
from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException

import app.core.sys.sys_calls_utils as scu
import app.core.sys.family_utils as fu
import app.misc.trust_utils as tutils
import app.core.sys.ecommerce_utils as ecut
import app.core.sys.task_utils as tku
import app.core.sys.agora_utils as agu
import app.core.sys.offer_utils as offu
import app.core.sys.routing_utils as ru


class AgoraCalls:

    @staticmethod
    @active_login
    async def _sys_call_list_ads(kernel, session, pars):
        return await AgoraCalls._agora_list_ads_safe(kernel, pars)


    #@staticmethod
    #@active_login
    #async def _sys_call_buy_object_title(kernel, session, pars):
    #    return await _agora_buy_object_safe(kernel, pars)


    @staticmethod
    @active_login
    async def _sys_call_buy_object_uri(kernel, session, pars):
        return await _agora_buy_object_uri_safe(kernel, pars)


    @staticmethod
    @active_login
    async def _sys_call_find_first_object_title(kernel, session, pars):
        return await _agora_find_first_object_title(kernel, pars)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def _agora_list_ads_safe(kernel, pars, t_id):
        return await AgoraCalls._agora_list_ads_impl(kernel, pars, t_id)


    @staticmethod
    async def _agora_list_ads_impl(kernel, pars, t_id):
        family_lev_ob = await scu.get_family_uplevel(kernel, pars, t_id)

        return await agu.family_list_ads(kernel, family_lev_ob, t_id)


#@federated_transaction(raise_if_fail = True)
#async def _agora_buy_object_safe(kernel, pars, t_id):
#    await agu._agora_buy_object_impl(kernel, pars, t_id)


@federated_transaction(raise_if_fail = True)
async def _agora_find_first_object_title(kernel, pars, t_id):
    return await agu.agora_find_first_object_title_impl(kernel, pars, t_id)
 

@federated_transaction(raise_if_fail = True)
async def _agora_buy_object_uri_safe(kernel, pars, t_id):
    return await agu._agora_buy_object_uri_impl(kernel, pars, t_id)
 
