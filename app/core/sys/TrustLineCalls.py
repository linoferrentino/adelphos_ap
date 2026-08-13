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


class TrustLineCalls:

    @staticmethod
    @active_login
    async def _sys_call_create(kernel, session, pars):
        alias_uri = session.alias_uri
        gCon.log(f"You want to create a trust line from {alias_uri}")
        gCon.log(f"pars {pars}")


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def tl_create_safe(kernel, actor_from, pars, t_id):
        pass
 
