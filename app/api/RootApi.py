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
from app.dao.AdInstanceDto import create_ad_instance
from datetime import datetime
import os
import re


def sudo_cmd(func):

    async def check_root(self):
        if (self.gateway.session.is_logged_root() == False):
            raise AdelphosException("You need to be root")

        return await func(self)
    
    return check_root


# this class users.
class AutoUsers:
    pass


class RootApi(BaseApi):

    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)
 

    # this is to allow the communication to a remote adelphos
    @sudo_cmd
    async def _hndl_allow_remote_adelphos(self):
        return await self._base_hndl_remote_adelphos(1, 'authorized')


    async def _base_hndl_remote_adelphos(self, new_flag, action):

        # first of all I have take the parameters
        remote_instance = self.gateway.get_param_safe('remote_adelphos')

        # Is the server already present? An adelphos instance is also an
        # activity pub server, so first of all I have to know if it is present
        ad_instance_dto = self.gateway.app.dao.ad_instance_dao.\
                get_from_hostname(remote_instance)

        now_time = datetime.now()

        if (ad_instance_dto is not None):

            if (ad_instance_dto.authorized == new_flag):
                return f"Remote instance {remote_instance} not changed"

            gCon.log(f"I want to change {ad_instance_dto.authorized} to {new_flag}")
            ad_instance_dto.authorized = new_flag
            ad_instance_dto.comment = f"Modified by root on {now_time}"
            self.gateway.app.dao.ad_instance_dao.update(ad_instance_dto)
            return f"Remote instance {remote_instance} {action}."

        # Ok, now I have to discover the actor at that instance.
        gCon.log(f"You want to authorize instance {remote_instance}")

        daemon_in_fediverse = f"@{USER_ID}@{remote_instance}"
        gCon.log(f"discovering actor {daemon_in_fediverse}")

        (daemon_server, daemon_actor) = await self.gateway.app.ap_api.\
                get_or_discover_actor(daemon_in_fediverse)

        # If I am here without exceptions I can create the row in Db.
        ad_instance_dto = create_ad_instance(daemon_actor.actor_id,
                                             1, f"{action} by root on {now_time}")
        self.gateway.app.dao.ad_instance_dao.store(ad_instance_dto)

        return f"OK, remote adelphos {daemon_in_fediverse} {action}"


    @sudo_cmd
    async def _hndl_deny_remote_adelphos(self):
        return await self._base_hndl_remote_adelphos(0, 'denied')


    # useful to have a peed at the db on the console.
    @sudo_cmd
    async def _hndl_dump_db(self):
        self.gateway.app.dao.db.dump_database()
        return "OK, dump created"


    async def _hndl_push_user(self):
        new_user = self.gateway.get_param_safe('alias')
        gCon.log(f"subsituting the user session with {new_user}")
        return await self.gateway.substitute_user(new_user)


    async def _hndl_pop_user(self):
        pass


    async def _hndl_apmkup_create_user(self):
        pass


    @sudo_cmd
    async def _hndl_play_script(self):
        script_file = self.gateway.get_param_safe('script')

        if (os.path.exists(script_file) == False):
            raise AdelphosException(f"Script {script_file} not found")

        with open(script_file, 'r') as file:
            for line in file:
                line = line.strip()
                if (len(line) == 0):
                    continue
                if (line[0] == '#'):
                    continue
                await self.gateway.outgress_result(f"executing: {line}")
                last_msg = await self.gateway.proc_request(line)

        return f"Exec script {script_file} done, last msg {last_msg}"


# here the handlers for this API
HANDLERS = {
     'sudo_adelphos_allow' : RootApi._hndl_allow_remote_adelphos,
     'sudo_adelphos_deny' : RootApi._hndl_deny_remote_adelphos,
     'sudo_dump_db' : RootApi._hndl_dump_db,
     'sudo_play_script': RootApi._hndl_play_script,
     'sudo_su_push': RootApi._hndl_push_user,
     'sudo_su_pop': RootApi._hndl_pop_user,
     'sudo_apmkup_create_user': RootApi._hndl_apmkup_create_user
}


