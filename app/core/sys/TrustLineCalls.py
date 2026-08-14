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


from app.api.UserSession import active_login
from app.core.algo.utils import federated_transaction
from app.logging import gCon
from app.sdc.Dependencies import Dependencies


class TrustLineCalls:

    @staticmethod
    @active_login
    async def _sys_call_create(kernel, session, pars):
        #alias_uri = session.alias_uri
        family_uri = session.family_uri
        pars['family_from'] = family_uri
        gCon.log(f"You want to create a trust line from {family_uri}")
        gCon.log(f"pars {pars}")
        await TrustLineCalls.tl_create_safe(kernel, pars)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def tl_create_safe(kernel, pars, t_id):

        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        family_to_ob = await fdb.uri_read_str(t_id, pars['family_to'],
                                           must_lock = True)
        gCon.log(f"Family to, its uri is: {family_to_ob().uri}")

        my_family = await fdb.uri_read_lock(t_id, pars['family_from'])

 
