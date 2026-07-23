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

from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from app.sdc.Dependencies import Dependencies
from app.core.algo.AliasAlgo import AliasAlgo
import app.misc.alias_utils as au


def sudo_cmd(func):

    async def check_root(kernel, session, pars):
        if (session.is_logged_root() == False):
            raise AdelphosException(AdErrno.EPERM, "You need to be root.")

        return await func(kernel, session, pars)
    
    return check_root



class RootApi:

    @sudo_cmd
    @staticmethod
    async def _sys_call_push_alias(kernel, session, pars):
        pass
 

    @sudo_cmd
    @staticmethod
    async def _sys_call_add_user(kernel, session, pars):

        social = kernel.get_dep(Dependencies.SOCIAL)
        user = pars['user']
        local_user = social.local_user_get(user, create_if_not_exists = False)
        if local_user is not None:
            raise AdelphosException(AdErrno.USER_ALREADY_EXISTING, user)
        local_user = social.local_user_get(user, create_if_not_exists = True)
        password = pars['password']
        trust = pars['trust']
        alias_name = pars['alias']

        (alias, family) = au.split_alias(alias_name, True)
        await AliasAlgo.alias_create(kernel,
                local_user.actor_dto.act.actor_id, alias, family, password, trust) 


    @sudo_cmd
    @staticmethod
    async def _sys_call_add_alias(kernel, session, pars):
        alias
