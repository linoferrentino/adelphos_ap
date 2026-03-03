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
from app.dao.AdelphosUri import EAdelphosType
from app.logging import gCon
from argon2 import PasswordHasher
from app.api.OutgressGateway import post_to_ap_actor
from app.dao.AdelphosUri import uriparse
import secrets
from datetime import datetime
from enum import IntEnum
from enum import auto
from app.dao.FamilyDto import family_dto_create_local
from app.dao.AliasDto import alias_dto_create_local




# This can be "myself" in the context, so that we can "speak" to ourselves
# in the adelphos federated world

# the API is a collection of "verbs".
# these verbs have for a "subject" an alias and an object can be an
# external entity.

# for example
# alias a1 buys object o1 belonging to alias a2
# in this case the subject is a1, the object is o1 and then there is a
# complement a2

# this division in subject-verb-object is the core of the adelphos api.

# as in Ancient Greek the subject is in the Nominative case
# the object is in the Accusative case
# the complement can be in the Genitive or in the Dative case

# so we have n_alias is the nominative alias
# n_instance, is the instance where he belongs
# and so on.

# n_alias is the first object that is instantiated.

# Can we have a family as a subject? Maybe yes. A family can merge
# with other families to for a group of a superior level.

# But in any case there is a user who has control of the family,
# we return basically to a user.

# the family cannot act independently, however it might seem that this
# is the case: for example we might see that a family merges or splits.
# But in this case the actor is the adelphos instance that does the action.

from app.api.BaseApi import BaseApi


class AliasApi(BaseApi):


    # The Alias Api can serve the Activity pub context or the Web socket context.
    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    def recv_token(self, token):
        if (token != self.gateway.session.token):
            raise AdelphosException("Invalid token")

        self.gateway.session.login_confirmed()
        return f"Token accepted, welcome to adelphos, \
                {self.gateway.session.uri.name}@{self.gateway.session.uri.family}"


    async def _hndl_login(self):
        alias = self.gateway.get_param_safe('alias')
        password = self.gateway.get_param_safe('password')

        alias_uri = uriparse(alias)

        gCon.log(f"You {alias_uri} want to login! {self}")

        msg = await self.login(alias_uri, password)

        return msg


    async def _hndl_put_token(self):
        token = self.gateway.get_param_safe('tk')
        return self.recv_token(token)


    async def login(self, uri, password):

        #self._set_uri(uri)

        if (uri.obj_type != EAdelphosType.ALIAS_TYPE):
            raise AdelphosException(f"type mismatch wanted alias got {uri.obj_type}")

        # first of all I get the family, the alias needs the family.
        family_dto = self.gateway.app.dao.family_dao\
                .get_from_local_name(uri.family) 

        if (family_dto is None):
            raise AdelphosException("Invalid alias/password")

        #self.gateway.session.family_dto = family_dto

        # the family has a name, the alias has also a nick.
        gCon.log(f"I have n_family {family_dto}")

        # OK, now I have to get the alias

        alias_dto = self.gateway.app.dao.alias_dao\
                .get_from_name_family_id(uri.name,
                                         family_dto.fd_actor_id)

        if (alias_dto is None):
            raise AdelphosException("Invalid alias/password")

        gCon.log(f"got the alias {alias_dto}, now we verify")

        ph = PasswordHasher()
        try:
            res = ph.verify(alias_dto.password, password)
        except:
            raise AdelphosException("Invalid username/password")

        #self.gateway.session.alias_dto = alias_dto

        # Now we are here, the alias is authenticated. Is there already a session
        # for this alias? If yes we try to know if it has expired, if not
        # we ask the user to force the logout from the other session

        # This maybe later, for now we simply do a memory session

        # OK, now we take the ActivityPub actor who is behind this alias
        actor_dto = self.gateway.app.dao.ap_actor_dao.get_from_local_id(
                alias_dto.actor_fk)

        if (actor_dto is None):
            raise Exception("Bug! there is not the actor corresponding")

        gCon.log(f"I will send the token to {actor_dto}")
        #self.gateway.session.actor_dto = actor_dto

        server_dto = self.gateway.app.dao.ap_server_dao.get_from_id(
                                            actor_dto.server_fk)

        if (server_dto is None):
            raise Exception("Bug! there is not the server corresponding")


        # OK, all the checks have passed! We can login.
        self.gateway.session.login_start(uri, family_dto, alias_dto,
                            server_dto, actor_dto)

        await post_to_ap_actor(self.gateway.app, server_dto, actor_dto,
f"Login OK, please copy the following line in adelphos chat\n\
put_token tk {self.gateway.session.token}")

        return """Login OK.
Please paste the line received
in your Mastodon inbox to finalize the login."""


#        self.gateway.session.server_dto = server_dto
#
#        # Now we have to get the server dto
#
#        # just a random token, and I also save a timestamp.
#        self.token = secrets.token_urlsafe()
#        self.session_age = datetime.now()
#
#        await post_to_ap_actor(self.gateway.app, server_dto, actor_dto,
#f"Login OK, please copy the following line in adelphos chat\n\
#put_token tk {self.token}")
#
#        self.user_state = EUserState.LOGGED_WITHOUT_TOKEN
#
#        return """Login OK.
#Please paste the line received
#in your Mastodon inbox to finalize the login."""


    def logout():
        pass


    def change_password():
        pass


# here the handlers for this API
HANDLERS = {
     'login' : AliasApi._hndl_login,
     'put_token' : AliasApi._hndl_put_token
}


