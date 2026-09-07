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
import app.core.sys.offer_utils as ofutils
import app.core.sys.sys_calls_utils as scu


class ObjectCalls:

    @staticmethod
    @active_login
    async def _sys_call_put_ad(kernel, session, pars):
        return await _object_put_ad_in_agora_safe(kernel, pars)
 

@federated_transaction(raise_if_fail = True)
async def _object_put_ad_in_agora_safe(kernel, pars ,t_id):
    family_ob = await scu.get_family_in_session(kernel, pars, t_id)
    alias_ob = await scu.get_alias_in_session(kernel, pars, t_id)
    await ofutils.object_put_ad_in_agora_impl(kernel, family_ob, alias_ob,
                                       pars, t_id)


