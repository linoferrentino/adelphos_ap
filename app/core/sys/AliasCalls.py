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
from argon2 import PasswordHasher
import app.misc.alias_utils as au
from app.sdc.Dependencies import Dependencies

from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.AdelphosUri import AdelphosUri

from app.core.algo.utils import federated_transaction
from app.logging import gCon

from app.api.UserSession import active_login

from app.exc.AdelphosException import AdErrno
from app.exc.AdelphosException import AdelphosException


class AliasCalls:

    @staticmethod
    @active_login
    async def _sys_call_send_msg(kernel, session, pars):
        pass


    @staticmethod
    @active_login
    async def _sys_call_logout(kernel, session, pars):
        session.logout()


    @staticmethod
    async def _sys_call_login(kernel, session, pars):
        login = pars['login']
        password = pars['password']

        await AliasCalls._session_login(kernel, session, login, password)

        return "Login OK, check your Mastodon inbox to get the token."


    @staticmethod
    async def _session_login(kernel, session, login, password, force = False):
        (alias, family) = au.split_alias(login)
        pars = {
          'alias' : alias,
          'family' : family,
          'password': password,
          'force' : force,
        }
        actor_handle = await AliasCalls.login_safe(kernel, pars)
        gCon.log(f"OK, the user {actor_handle} has logged in with alias {alias}")
        social_dao = kernel.get_dep(Dependencies.SOCIAL_DAO)
        actor_dto = social_dao.actor_get_from_actor_handle(actor_handle)
        token = session.login_start(alias, family, actor_dto, force)

        if force == True:
            return

        social = kernel.get_dep(Dependencies.SOCIAL)
        await social.out_msg_listener_to_actor(actor_dto,
                f"Copy this command to finalize login 'alias.put_token tk {token}'")


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
        return await AliasCalls._login_impl(kernel, pars, t_id)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def login_safe(kernel, pars, t_id):
        return await AliasCalls._login_impl(kernel, pars, t_id)


    @staticmethod
    async def _login_impl(kernel, pars, t_id):
        alias = pars['alias']
        family = pars['family']
        password = pars['password']
        force = pars['force']

        alias_uri = AdelphosUri(EAdelphosType.ALIAS_TYPE, alias, family = family)
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

        gCon.log(f"Searching alias {alias_uri}")
        alias_ob = await fdb.uri_read_no_lock(t_id, alias_uri, True)

        if alias_ob is None:
            raise AdelphosCoreException(ECoreErrno.EINVALID_USER_OR_PASSWORD,
                                        f"{alias}.{family}")

        if force == False:
            password_hashed = alias_ob().get_scalar('password')

            ph = PasswordHasher()
            try:
                res = ph.verify(password_hashed, password)
            except:
                raise AdelphosCoreException(ECoreErrno.EINVALID_USER_OR_PASSWORD,
                                        f"{alias}.{family}")

        return alias_ob().get_scalar('actor_handle')


