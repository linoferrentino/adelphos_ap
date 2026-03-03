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
#
# This is the API that only root can call.


from app.api.AdelphosException import AdelphosException
from app.api.BaseApi import BaseApi
from app.logging import gCon
from app.consts import USER_ID


def sudo_cmd(func):

    async def check_root(self):
        if (self.gateway.session.is_logged_root() == False):
            raise AdelphosException("You need to be root")

        return await func(self)
    
    return check_root


class RootApi(BaseApi):

    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)
 

    # this is to allow the communication to a remote adelphos
    @sudo_cmd
    async def _hndl_allow_remote_adelphos(self):
        # first of all I have take the parameters
        remote_instace = self.gateway.get_param_safe('remote_adelphos')

        # Is the instance already present?

        # Is the instance already allowed?

        # Ok, now I have to discover the actor at that instance.
        gCon.log(f"You want to authorize instance {remote_instace}")

        daemon_in_fediverse = f"@{USER_ID}@{remote_instace}"
        gCon.log(f"discovering actor {daemon_in_fediverse}")

        (daemon_server, daemon_actor) = await self.gateway.app.ap_api.\
                get_or_discover_actor(daemon_in_fediverse)

        # If I am here without exceptions I can create the row in Db.

        return f"OK, remote adelphos {daemon_in_fediverse} allowed"


    @sudo_cmd
    async def _hndl_deny_remote_adelphos(self):
        return "OK, remote adelphos denied"


    # useful to have a peed at the db on the console.
    @sudo_cmd
    async def _hndl_dump_db(self):
        pass


# here the handlers for this API
HANDLERS = {
     'sudo_adelphos_allow' : RootApi._hndl_allow_remote_adelphos,
     'sudo_adelphos_deny' : RootApi._hndl_deny_remote_adelphos,
     'sudo_dump_db' : RootApi._hndl_dump_db
}


