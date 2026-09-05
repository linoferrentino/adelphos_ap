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
import json
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
        await _root_play_script(kernel, session, pars)



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
        return session.client.pop_session()


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
        await _get_user_impl(kernel, session, pars, create = True)


    @sudo_cmd
    @staticmethod
    async def _sys_call_add_user_alias(kernel, session, pars):
        return await _sys_call_add_user_alias_impl(kernel, session, pars,
                                create = True)


    @sudo_cmd
    @staticmethod
    async def _sys_call_add_alias(kernel, session, pars):
        return await _sys_call_add_user_alias_impl(kernel, session, pars,
                                create = False)



async def _sys_call_add_user_alias_impl(kernel, session, pars,
                                        *, create = True):
    local_user = await _get_user_impl(kernel, session, pars, create = create)

    alias = pars['alias']

    (alias_name, family) = au.split_alias(alias, True)

    pars['actor_id'] = local_user.actor_dto.act.actor_id
    pars['alias_name'] = alias_name
    pars['family']  = family
    pars['user_handle'] = local_user.actor_dto.get_social_handle()

    return await AliasAlgo.alias_create_safe(kernel, pars) 


async def _get_user_impl(kernel, session, pars, *, create = False):
    social = kernel.get_dep(Dependencies.SOCIAL)
    user = pars['user']
    local_user = social.local_user_get(user, create_if_not_exists = False)
    if create == False and local_user is None:
        raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST, user)
    elif create == False:
        return local_user
    if local_user is not None:
        raise AdelphosException(AdErrno.USER_ALREADY_EXISTING, user)
    local_user = social.local_user_get(user, create_if_not_exists = True)
    return local_user


async def _root_play_line(kernel, session, pars, line):
    if "==>" in line:
        (data, exps) = line.split("==>")
        exp = json.loads(exps)
    else:
        data = line
        exp = {
                'errno' : 0
        }
    gCon.log(f"Play line |{data}| with exp |{exp}|")
    res_str = await session.client.direct_gateway_call(data)
    gCon.log(f"result {res_str}")
    res_ob = json.loads(res_str)
    if (res_ob['errno'] != exp['errno']):
        raise AdelphosException(AdErrno.ESCRIPT_ERROR, res_str)
    exp_re = exp.get('res_re')
    if exp_re is None:
        return
    if re.search(exp_re, res_ob['res']) is None:
        raise AdelphosException(AdErrno.ESCRIPT_ERROR, f"Not found {exp_re} in {res_ob['res']}")


async def _root_play_script(kernel, session, pars):
    gCon.log(f"Playing the script {pars['script_path']}")
    with open (f"tests/scripts/{pars['script_path']}.as") as script:
        multiline = False
        long_line = ""
        for line in script:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            if line[-1] == "\\":
                multiline = True
                long_line += line[:-1]
                continue
            if multiline:
                long_line += line
            else:
                long_line = line
                
            await _root_play_line(kernel, session, pars, long_line)

