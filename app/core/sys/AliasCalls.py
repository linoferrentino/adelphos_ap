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

from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException
from app.sdc.Dependencies import Dependencies

from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.AdelphosUri import AdelphosUri

from app.core.algo.utils import federated_transaction
from app.logging import gCon

from app.api.UserSession import active_login

from app.exc.AdelphosException import AdErrno
from app.exc.AdelphosException import AdelphosException

import app.core.sys.sys_calls_utils as scu
import app.core.sys.alias_utils as au
import app.core.sys.task_utils as tku
import app.core.ui.msg_descs as mdescs
import app.core.sys.social_utils as su


class AliasCalls:

    @staticmethod
    @active_login
    async def _sys_call_send_msg(kernel, session, pars):
        await _sys_call_send_msg_safe(kernel, pars)


    @staticmethod
    @active_login
    async def _sys_call_logout(kernel, session, pars):
        session.logout()


    @staticmethod
    async def _sys_call_login(kernel, session, pars):
        await session_login_safe(kernel, pars)
        return "Login OK, check your Mastodon inbox to get the token."


    @staticmethod
    async def _sys_call_put_token(kernel, session, pars):
        token = pars['tk']
        session.accept_token(token)
        return f"Login OK, welcome to adelphos, {session.alias_family}."


    @staticmethod
    @active_login
    async def _sys_call_whoami(kernel, session, pars):
        res = {
                'active_login' : session.alias_family
              }
        return res

 
    @staticmethod
    @federated_transaction(raise_if_fail = False)
    async def login(kernel, pars, t_id):
        return await au._login_impl(kernel, pars, t_id)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def login_safe(kernel, pars, t_id):
        return await au._login_impl(kernel, pars, t_id)


    @staticmethod
    @active_login
    async def _sys_call_tasks_as_dikastes(kernel, session, pars):
        pars['_as_role'] = 'dikastes'
        return await _get_tasks_of_type_safe(kernel, pars)


    @staticmethod
    @active_login
    async def _sys_call_tasks_as_diakonos(kernel, session, pars):
        pars['_as_role'] = 'diakonos'
        return await _get_tasks_of_type_safe(kernel, pars)


@federated_transaction(raise_if_fail = True)
async def _sys_call_send_msg_safe(kernel, pars, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    alias_to_uri_pars = pars['alias_to']
    alias_to_ob = await fdb.uri_read_str(t_id, alias_to_uri_pars)
    alias_to_uri = alias_to_ob().uri.unparse()
    alias_from_uri = pars['_param'].alias_uri_str
    msg = await mdescs.build_message_from_alias(pars['msg'], alias_from_uri, alias_to_uri)
    await su.out_msg_to_alias_ob(kernel, alias_to_ob, msg, t_id)


@federated_transaction(raise_if_fail = True)
async def session_login_safe(kernel, pars, t_id):
    login = pars['login']
    password = pars['password']
    session = pars['_param']

    await au._session_login(kernel, session, login, password, 
                                    t_id)


@federated_transaction(raise_if_fail = True)
async def _get_tasks_of_type_safe(kernel, pars, t_id):
    return await tku._get_tasks_of_type_impl(kernel, pars, t_id)


