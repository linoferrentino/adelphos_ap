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

import app.misc.utils as misc


class AdelphosInitDaemon(Daemon):

    def __init__(self, kernel):
        super().__init__(kernel)


    async def _create_remote_root(self, root_handle, root_password,
                                  already_hashed):
        sg = self.get_dep(Dependencies.SOCIAL_GATEWAY)
        root_actor = await sg.discover_user(root_handle)
        if already_hashed is None:
            already_hashed = True
        gCon.log(f"Remote root actor {root_actor} hashed passwd {already_hashed}")
        await self._create_root_alias(root_handle,
                                      root_password, already_hashed)


    async def _create_local_root(self, local_user, root_password, already_hashed):
        social = self.get_dep(Dependencies.SOCIAL)
        root_user = social.local_user_get(local_user, create_if_not_exists = True)
        if already_hashed is None:
            already_hashed = False
        gCon.log(f"Local root {root_user}, already hashed {already_hashed}")
        await self._create_root_alias(root_user.actor_dto.get_social_handle(),
                                      root_password, already_hashed)


    async def _create_root_alias(self, root_user, root_password,
                                 already_hashed):
        pars = {
            'user_handle' : root_user,
            'alias_name' : 'root',
            'family' : 'admins',
            'password' : root_password,
            'already_hashed' : already_hashed,
            'my_trust' : 5,
            'maybe' : True
        }

        res = await AliasAlgo.alias_create(self.kernel, pars)

        if res != ECoreErrno.DONE_OK:
            gCon.log(f"res error {res} creating root alias")
            raise Exception(f"res error {res} creating root alias")
        gCon.log(f"created the root {root_user}")


    async def start_impl(self):
        conf_general = self.conf.get_conf('general')
        root_handle = conf_general['root']
        root_password = conf_general['root_password']
        already_hashed = conf_general.get('already_hashed', None)

        local_user = misc.get_local_alias(root_handle)
        if local_user is not None:
            gCon.log(f"Root is the local user {local_user}, hashed {already_hashed}")
            await self._create_local_root(local_user,
                        root_password, already_hashed)
        else:
            gCon.log(f"root is {root_handle}, hashed {already_hashed}")
            await self._create_remote_root(root_handle,
                            root_password, already_hashed)


    async def stop_impl(self):
        pass


