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

from app.logging import gCon
from app.core.algo.utils import federated_transaction
from app.sdc.Dependencies import Dependencies
from app.federation.FederatedUri import FederatedUri

from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors

class FederatedRPCs:

    @staticmethod
    async def _sys_call_return(kernel, actor_from, pars):
        await FederatedRPCs._sys_call_return_impl(kernel, actor_from, pars)


    @staticmethod
    async def _sys_call_return_no_mod(kernel, actor_from, pars):
        await FederatedRPCs._sys_call_return_impl(kernel, actor_from, pars)


    @staticmethod
    async def _sys_call_return_impl(kernel, actor_from, pars):
        uri_str = pars['uri_str']
        obstr = pars.get('obstr')
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        gCon.rule(f"[blue]{fdb.hostname}: _sys_call_return_impl got {uri_str} in return[/blue]")
        t_id = fdb.begin_transaction()
        await fdb.return_object_received(t_id, uri_str, obstr)
        fdb.commit_transaction(t_id)


    @staticmethod
    async def _sys_call_borrow(kernel, actor_from, pars):
        return await _sys_call_borrow_safe(kernel, pars)



@federated_transaction(raise_if_fail = True)
async def _sys_call_borrow_safe(kernel, pars, t_id):

    actor_from = pars['_param']
    uri_str = pars['uri_str']
    lock = pars['lock']
    social_handle = actor_from.get_social_handle()
    gCon.log(f"Read for the {uri_str} with lock {lock} from {social_handle}")

    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    fob = await fdb.uri_read_str(t_id, uri_str, must_lock = lock)

    fob_str = fob().to_store_str()
    gCon.log(f"{uri_str} is: {fob_str}")

    if lock == True:
        fob().lent_to(social_handle)

    return {
            'obstr' : fob_str
    }

