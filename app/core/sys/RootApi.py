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
from app.core.sys.AliasCalls import AliasCalls
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
    async def _sys_call_play_script(kernel, session, pars):
        gCon.log(f"Playing the script {pars['script_path']}")
        with open (f"tests/scripts/{pars['script_path']}") as script:
            for line in script:
                line = line.strip()
                if len(line) == 0:
                    continue
                exp = None
                if line[0] == '#':
                    continue
                if "==>" in line:
                    (data, exp) = line.split("==>")
                else:
                    data = line
                gCon.log(f"Play line {data} with exp {exp}")
                response = await session.client.direct_gateway_call(data)
                gCon.log(f"result {response}")



    @sudo_cmd
    @staticmethod
    async def _sys_call_allow_remote(kernel, session, pars):
        host = pars['host']
        social_api = kernel.get_dep(Dependencies.SOCIAL_API)
        user_tag = social_api.remote_host_allow(host)


    @sudo_cmd
    @staticmethod
    async def _sys_call_deny_remote(kernel, session, pars):
        host = pars['host']
        social_api = kernel.get_dep(Dependencies.SOCIAL_API)
        user_tag = social_api.remote_host_deny(host)


    @staticmethod
    async def _sys_call_pop_alias(kernel, session, pars):
        session.client.pop_session()


    @sudo_cmd
    @staticmethod
    async def _sys_call_push_alias(kernel, session, pars):
        alias = pars['alias']
        alias_session = session.client.push_session(alias)
        await AliasCalls._session_login(kernel, alias_session,
                                        alias, None, True)
        return alias_session.get_alias_ob().ob.fields


    @sudo_cmd
    @staticmethod
    async def _sys_call_add_user(kernel, session, pars):
        await RootApi._add_user_impl(kernel, session, pars)


    async def _add_user_impl(kernel, session, pars):
        social = kernel.get_dep(Dependencies.SOCIAL)
        user = pars['user']
        local_user = social.local_user_get(user, create_if_not_exists = False)
        if local_user is not None:
            raise AdelphosException(AdErrno.USER_ALREADY_EXISTING, user)
        local_user = social.local_user_get(user, create_if_not_exists = True)
        return local_user
 

    @sudo_cmd
    @staticmethod
    async def _sys_call_add_user_alias(kernel, session, pars):
        local_user = await RootApi._add_user_impl(kernel, session, pars)

        alias = pars['alias']

        (alias_name, family) = au.split_alias(alias, True)

        pars['actor_id'] = local_user.actor_dto.act.actor_id
        pars['alias_name'] = alias_name
        pars['family']  = family
        pars['user_handle'] = local_user.actor_dto.get_social_handle()

        await AliasAlgo.alias_create(kernel, pars) 

