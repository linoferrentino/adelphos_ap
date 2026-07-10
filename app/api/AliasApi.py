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
# This is the class that models an Alias with its business logic
from app.api.AdelphosException import AdelphosException
from app.api.AdelphosException import EAdelhposErrno
from app.dao.AdelphosUri import EAdelphosType
from app.logging import gCon
from argon2 import PasswordHasher
from app.api.OutgressGateway import post_to_ap_actor
from app.dao.AdelphosUri import uriparse
import secrets
from datetime import datetime
from enum import IntEnum
from enum import auto
from app.api.UserSession import active_login

from app.api.BaseApi import BaseApi
from app.api.BaseApi import only_in_debug


#class AliasApi:
#
#    @staticmethod
#    async def _sys_call_login(kernel, session, pars):
#        login = pars['login']
#        password = pars['password']
#
#        return "LOGIN OK"


class AliasApi_deprecated(BaseApi):


    # The Alias Api can serve the Activity pub context or the Web socket context.
    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    def recv_token(self, token):
        res = self.gateway.session.accept_token(token)
        if (res == False):
            raise AdelphosException("Invalid token or not logged in.")

        return f"Token accepted, welcome to adelphos, \
                {self.gateway.session.uri.name}@{self.gateway.session.uri.family}"


    async def _hndl_login(self):
        await self._hndl_base_login()
        await self.gateway.post_to_logged_user_inbox(
f"Login OK, please copy the following line in adelphos chat\n\
put_token tk {self.gateway.session.token}")
        return """Login OK.
Please paste the line received
in your Mastodon inbox to finalize the login."""


    # test login without MFA, this is only enabled in tests.
    @only_in_debug
    async def _hndl_login_1f(self):
        await self._hndl_base_login()
        self.gateway.session.force_token()
        return 'Login OK.'


    async def _hndl_base_login(self):
        alias = self.gateway.get_param_safe('alias')
        await self._hndl_login_alias(alias)


    async def _hndl_login_alias(self, alias):
        password = self.gateway.get_param_safe('password')
        # if I pass here without exception I have done the login.
        await self.login_str(alias, password, False)


    async def _hndl_put_token(self):
        token = self.gateway.get_param_safe('tk')
        return self.recv_token(token)


    async def force_login(self, alias_str):
        await self.login_str(alias_str, None, True)
        self.gateway.session.force_token()


    # login from a string.
    async def login_str(self, alias_str, password, force: bool):
        alias_uri = uriparse(alias_str)
        msg = await self.login(alias_uri, password, force)
        return msg


    # if force the login is granted without password
    async def login(self, uri, password, force):

        if (uri.obj_type != EAdelphosType.ALIAS_TYPE):
            raise AdelphosException(f"type mismatch wanted alias got {uri.obj_type}")


        # first of all I check the existence
        self.gateway.kernel.aa.alias_algo.login_or_die(
                uri.name, uri.family, password, force)

        # If I am here all is OK
        assert False


        # first of all I get the family, the alias needs the family.
        family_dto = self.gateway.app.dao.family_dao\
                .get_from_local_name(uri.family) 

        if (family_dto is None):
            #gCon.log(f"there is not a family {uri.family}")
            raise AdelphosException("Invalid username/password",
                        EAdelhposErrno.EINVALID_USER_OR_PASSWORD)

        #self.gateway.session.family_dto = family_dto

        # the family has a name, the alias has also a nick.
        #gCon.log(f"I have family {family_dto}")

        # OK, now I have to get the alias

        alias_dto = self.gateway.app.dao.alias_dao\
                .get_from_name_family_id(uri.name,
                                         family_dto.fd_actor_id)

        if (alias_dto is None):
            raise AdelphosException("Invalid alias/password",
                                   EAdelhposErrno.EINVALID_USER_OR_PASSWORD)

        #gCon.log(f"got the alias {alias_dto}, now we verify")

        if (force == False):
            ph = PasswordHasher()
            try:
                res = ph.verify(alias_dto.password, password)
            except:
                raise AdelphosException("Invalid username/password",
                                   EAdelhposErrno.EINVALID_USER_OR_PASSWORD)

        # OK, now we take the ActivityPub actor who is behind this alias
        actor_dto = self.gateway.app.dao.ap_actor_dao.get_from_local_id(
                alias_dto.actor_fk)

        if (actor_dto is None):
            raise AdelphosException\
        (f"Bug! there is not the actor corresponding {uri.name}",
         EAdelhposErrno.EBADDB)

        #gCon.log(f"I will send the token to {actor_dto}")

        server_dto = self.gateway.app.dao.ap_server_dao.get_from_id(
                                            actor_dto.server_fk)

        if (server_dto is None):
            raise Exception("Bug! there is not the server corresponding")

        # OK, all the checks have passed! We can login.
        self.gateway.session.login_start(uri, family_dto, alias_dto,
                            server_dto, actor_dto)



    def logout():
        pass


    def change_password():
        pass


    # the backdoor is only enabled in debug and it grants root access without
    # 2fa with the same root password, use with care!
    @only_in_debug
    async def _hndl_backdoor(self):
        # the login is the same, but we force the receive of the token
        await self._hndl_login_alias("##root.admins")
        self.gateway.session.force_token()
        return "Backdoor OK, you are root"


    @active_login
    async def _hndl_whoami(self):
        return self.gateway.session.whoami()


# here the handlers for this API
HANDLERS = {
     'login' : AliasApi._hndl_login,
     'al_login1f' : AliasApi._hndl_login_1f,
     'put_token' : AliasApi._hndl_put_token,
     'backdoor' : AliasApi._hndl_backdoor,
     'whoami': AliasApi._hndl_whoami,
}


