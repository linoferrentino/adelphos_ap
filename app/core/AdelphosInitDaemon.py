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
from app.core.Daemon import Daemon
from app.logging import gCon
from app.sdc.Dependencies import Dependencies

LOCAL_REX = r":local:(\w*)"


class AdelphosInitDaemon(Daemon):

    def __init__(self, kernel):
        super().__init__(kernel)


    async def _create_local_root(self, local_user, root_password):
        social = self.get_dep(Dependencies.SOCIAL)
        local_user = social.local_user_get(local_user, create_if_not_exists = True)
        gCon.log(f"local user {local_user}")


    async def start_impl(self):
        root_handle = self.conf.get_conf('general')['root']
        root_password = self.conf.get_conf('general')['root_password']
        gCon.log(f"creating root {root_handle}")
        local_user_mt = re.match(LOCAL_REX, root_handle)
        if local_user_mt is not None:
            local_user = local_user_mt.group(1)
            gCon.log(f"Root is the local user {local_user}")
            await self._create_local_root(local_user, root_password)
        else:
            gCon.log(f"root is {root_handle}")
            await self._create_remote_root(root_handle, root_password)


    async def stop_impl(self):
        pass


