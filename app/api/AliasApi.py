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
import secrets
from datetime import datetime
from enum import IntEnum
from enum import auto


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


# these are the states for the user.
class EUserState(IntEnum):
    NOT_LOGGED = auto()
    LOGGED_WITHOUT_TOKEN = auto()
    LOGGED_AND_TOKEN = auto()


class AliasApi:


    # an alias can be built with an uri, or a string (which is then parsed)
    def __init__(self, ctx):
        self.ctx = ctx
        self.user_state = EUserState.NOT_LOGGED


    def _set_uri(self, uri):
        self.uri = uri
        if (uri.obj_type != EAdelphosType.ALIAS_TYPE):
            raise AdelphosException(f"type mismatch wanted alias got {uri.obj_type}")


    # this method will login the LOCAL alias.
    # it verifies the password and, if it matches, it sends to the actor
    # an OTP code which is used to finalize the login

    # login is a verb: it has only a subject.

    def is_logged_in(self ):
        if (self.user_state != EUserState.LOGGED_AND_TOKEN):
            gCon.log(f"No logged {self.user_state}")
            return False
        gCon.log(f"YES logged {self.user_state}")
        return True


    def recv_token(self, token):
        if (token != self.token):
            raise AdelphosException("Invalid token")
        self.user_state = EUserState.LOGGED_AND_TOKEN
        return f"Token accepted, welcome to adelphos, {self.uri.name}."


    async def login(self, uri, password):

        self._set_uri(uri)

        # first of all I get the family, the alias needs the family.
        self.n_family_dto = self.ctx.app.dao.family_dao\
                .get_from_local_name(self.uri.family) 

        if (self.n_family_dto is None):
            raise AdelphosException("Invalid alias/password")

        # the family has a name, the alias has also a nick.
        gCon.log(f"I have n_family {self.n_family_dto}")

        # OK, now I have to get the alias

        self.n_alias_dto = self.ctx.app.dao.alias_dao\
                .get_from_name_family_id(self.uri.name,
                                         self.n_family_dto.fd_actor_id)

        if (self.n_alias_dto is None):
            raise AdelphosException("Invalid alias/password")

        gCon.log(f"got the alias {self.n_alias_dto}, now we verify")

        ph = PasswordHasher()
        try:
            res = ph.verify(self.n_alias_dto.password, password)
        except:
            raise AdelphosException("Invalid username/password")

        # Now we are here, the alias is authenticated. Is there already a session
        # for this alias? If yes we try to know if it has expired, if not
        # we ask the user to force the logout from the other session

        # This maybe later, for now we simply do a memory session

        # OK, now we take the ActivityPub actor who is behind this alias
        self.n_actor_dto = self.ctx.app.dao.ap_actor_dao.get_from_local_id(
                self.n_alias_dto.actor_fk)

        if (self.n_actor_dto is None):
            raise AdelphosException("Bug! there is not the actor corresponding")

        gCon.log(f"I will send the token to {self.n_actor_dto}")
        self.n_server_dto = self.ctx.app.dao.server_dao.get_from_id(
                                            self.n_actor_dto.server_fk)

        if (self.n_server_dto is None):
            raise AdelphosException("Bug! there is not the server corresponding")

        # Now we have to get the server dto

        # just a random token, and I also save a timestamp.
        self.token = secrets.token_urlsafe()
        self.session_age = datetime.now()

        await post_to_ap_actor(self.ctx, self.n_server_dto,
                               self.n_actor_dto,
f"Login OK, please copy the following line in adelphos chat\n\
put_token tk {self.token}")

        self.user_state = EUserState.LOGGED_WITHOUT_TOKEN

        return "Login OK\nplease paste the line received\
in your Mastodon inbox to finalize the login."


    def logout():
        pass


    def change_password():
        pass


    # this does not belong here!

    # this is the function to buy an object, it will make the routing and create
    # all the cheques.
    # it returns a path or None if some conditions are not met.
    def buy_object_or_service(object_sold):

        # this is a path.
        # the place and time of the object
        # the price you will pay, in t0 or tX money
        # the currency, etc.
        
        return "The object will arrive at @place@iii on Wednesday March 15th"
