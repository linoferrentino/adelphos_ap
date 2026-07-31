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
    async def _sys_call_read(kernel, actor_from, pars):
        uri_str = pars['uri_str']
        gCon.log(f"GOT the read for the {uri_str}")


        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

        uri_ob = fdb.parse_uri(uri_str)
        gCon.log(f"the uri ob is {uri_ob}")

        t_id = await fdb.begin_transaction()
        fob = await fdb.uri_read_lock(t_id, uri_ob, maybe = True)
        gCon.log(f"the ob is {fob()}")
        if fob is not None:
            fob_str = fob().to_store_str()
            gCon.log(f"returning string {fob_str}")
            return {
                    'obstr' : fob_str
            }
        return None


 
