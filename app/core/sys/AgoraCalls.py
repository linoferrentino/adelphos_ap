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


from app.core.algo.utils import federated_transaction
from app.logging import gCon
from app.api.UserSession import active_login
import app.core.sys.sys_calls_utils as scu
from app.sdc.Dependencies import Dependencies


class AgoraCalls:

    @staticmethod
    @active_login
    async def _sys_call_list_ads(kernel, session, pars):
        pars['_session'] = session
        return await AgoraCalls._agora_list_ads_safe(kernel, pars)
 

    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def _agora_list_ads_safe(kernel, pars, t_id):
        return await AgoraCalls._agora_list_ads_impl(kernel, pars, t_id)


    @staticmethod
    async def _agora_list_ads_impl(kernel, pars, t_id):
        family_lev_ob = await scu.get_family_uplevel(kernel, pars, t_id)
        gCon.log(f"The family upleveled is {family_lev_ob().ob.fields}")
        agora_uri = family_lev_ob().get_scalar('agora')
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        agora_ob = await fdb.uri_read_str(t_id, agora_uri, must_lock = True)
        offers = agora_ob().get_as_list('offers')
        return offers


