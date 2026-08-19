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
from app.core.ECoreErrno import ECoreErrno
from app.sdc.Dependencies import Dependencies
from app.core.algo.AliasAlgo import AliasAlgo

#LOCAL_REX = r":local:(\w*)"
import app.misc.alias_utils as au


class AdelphosInitDaemon(Daemon):

    def __init__(self, kernel):
        super().__init__(kernel)


    async def _create_remote_root(self, root_handle, root_password):
        sg = self.get_dep(Dependencies.SOCIAL_GATEWAY)
        root_actor = await sg.discover_user(root_handle)
        gCon.log(f"Found the remote root actor {root_actor}")
        await self._create_root_alias(root_handle,
                                      root_actor.act.actor_id,
                                      root_password)


    async def _create_local_root(self, local_user, root_password):
        social = self.get_dep(Dependencies.SOCIAL)
        root_user = social.local_user_get(local_user, create_if_not_exists = True)
        await self._create_root_alias(local_user,
                                      root_user.actor_dto.act.actor_id,
                                      root_password)


    async def _create_root_alias(self, root_user, root_actor_id, root_password):
        pars = {
            'actor_id' : root_actor_id,
            'user_handle' : root_user,
            'alias_name' : 'root',
            'family' : 'admins',
            'password' : root_password,
            'maybe' : True
        }

        res = await AliasAlgo.alias_create(self.kernel, pars)

        if res != ECoreErrno.DONE_OK:
            gCon.log(f"res error {res} creating root alias")
            raise Exception(f"res error {res} creating root alias")
        gCon.log(f"created the root {root_user} with id {root_actor_id}")


    async def start_impl(self):
        root_handle = self.conf.get_conf('general')['root']
        root_password = self.conf.get_conf('general')['root_password']
        local_user = au.get_local_alias(root_handle)
        if local_user is not None:
            gCon.log(f"Root is the local user {local_user}")
            await self._create_local_root(local_user, root_password)
        else:
            gCon.log(f"root is {root_handle}")
            await self._create_remote_root(root_handle, root_password)


    async def stop_impl(self):
        pass


