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
from app.sdc.Dependencies import Dependencies
from app.federation.FederatedUri import FederatedUri


class FederatedRPCs:

    @staticmethod
    async def _sys_call_return(kernel, actor_from, pars):
        uri_str = pars['uri_str']
        obstr = pars['obstr']
        gCon.log(f"[red]Got the return for object {uri_str} = {obstr}[/red]")
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

        t_id = fdb.begin_transaction()
        await fdb.return_object_received(t_id, uri_str, obstr)
        fdb.commit_transaction(t_id)


    @staticmethod
    async def _sys_call_borrow(kernel, actor_from, pars):
        uri_str = pars['uri_str']
        lock = pars['lock']
        social_handle = actor_from.get_social_handle()
        gCon.log(f"Read for the {uri_str} with lock {lock} from {social_handle}")

        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

        t_id = fdb.begin_transaction()
        fob = await fdb.uri_read_str(t_id, uri_str,
                                     must_lock = lock,
                                     maybe = True)
        if fob is None:
            return None

        fob_str = fob().to_store_str()
        gCon.log(f"returning string {fob_str}")

        if lock == True:
            fob().lent_to(social_handle)
            gCon.log("======================= finalizing lending ")
            fdb.commit_transaction(t_id)
        else:
            fdb.rollback_transaction(t_id)

        return {
                'obstr' : fob_str
        }
