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

class AliasCalls:

    @staticmethod
    async def _sys_call_login(kernel, session, pars):
        login = pars['login']
        password = pars['password']
        (alias, family) = au.split_alias(login)
        actor_id = await AliasCalls.login_safe(kernel, alias, family, password)
        gCon.log(f"login ok for actor {actor_id}")
        social_dao = kernel.get_dep(Dependencies.SOCIAL_DAO)
        actor_dto = social_dao.actor_get_from_id(actor_id)
        gCon.log(f"login OK for {actor_dto}")
        token = session.login_start(alias, family, actor_dto)
        social = kernel.get_dep(Dependencies.SOCIAL)
        await social.out_msg_listener_to_actor(actor_dto,
                f"Copy this command to finalize login 'alias.put_token tk {token}'")
        return "Login OK, check your Mastodon inbox to get the token."


    @staticmethod
    async def _sys_call_put_token(kernel, session, pars):
        token = pars['tk']
        session.accept_token(token)
        return f"Login OK, welcome to adelphos, {session.alias_family}."

 
    @staticmethod
    @federated_transaction(raise_if_fail = False)
    async def login(kernel, alias, family, password, t_id):
        return await AliasCalls._login_impl(kernel, alias, family, password, t_id)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def login_safe(kernel, alias, family, password, t_id):
        return await AliasCalls._login_impl(kernel, alias, family, password, t_id)


    async def _login_impl(kernel, alias, family, password, t_id):

        alias_uri = AdelphosUri(EAdelphosType.ALIAS_TYPE, alias, family = family)
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        gCon.log(f"checking uri {alias_uri}")

        alias_ob = await fdb.uri_read_no_lock(t_id, alias_uri, True)

        if alias_ob is None:
            raise AdelphosCoreException(ECoreErrno.EINVALID_USER_OR_PASSWORD,
                                        f"{alias}.{family}")

        gCon.log(f"checking login for {alias_ob()}")
        password_hashed = alias_ob().get_primitive_value('password')

        ph = PasswordHasher()
        try:
            res = ph.verify(password_hashed, password)
        except:
            raise AdelphosCoreException(ECoreErrno.EINVALID_USER_OR_PASSWORD,
                                    f"{alias}.{family}")
        return alias_ob().val('actor_id')

