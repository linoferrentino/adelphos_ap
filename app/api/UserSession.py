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

# this is the session that holds data of the current user.
# this is used by the WebSocket, as the ActivityPub Gateway is stateless.
# the session for now is not persistent.

# if you logout it is recreated.
import secrets
from datetime import datetime
from enum import IntEnum
from enum import auto

# these are the states for the user.
class EUserState(IntEnum):
    NOT_LOGGED = auto()
    LOGGED_WITHOUT_TOKEN = auto()
    LOGGED_AND_TOKEN = auto()


# the user session stores all the data that is accumulating during the
# conversation with the user.
class UserSession:


    def __init__(self, gateway):

        self.gateway = gateway

        # the data relative to the logged user
        self.uri = None
        self.family_dto = None
        self.alias_dto  = None
        self.actor_dto = None
        self.server_dto = None

        # this is the data relative to the session.
        self.session_age = None
        self.token = None

        self.user_state = EUserState.NOT_LOGGED


    def accept_token(self, token):
        # Am I in the right state?
        if (self.user_state != EUserState.LOGGED_WITHOUT_TOKEN):
            return False
        if (self.token != token):
            return False
        self.user_state = EUserState.LOGGED_AND_TOKEN
        return True


    # this is called when we are sure that the user can login.
    def login_start(self, uri, family_dto, alias_dto, server_dto, actor_dto):

        self.uri = uri
        self.family_dto = family_dto
        self.alias_dto = alias_dto
        self.server_dto = server_dto
        self.actor_dto = actor_dto

        # here I will extract the notifications from the DB, if someone has
        # asked me a trust line or something.
        self.token = secrets.token_urlsafe()
        self.session_age = datetime.now()

        self.user_state = EUserState.LOGGED_WITHOUT_TOKEN


    def post_login_data(self):
        # here
        pass


    def is_login_valid(self):
        if (self.user_state != EUserState.LOGGED_AND_TOKEN):
            return False
        # let's get the age
        time_now = datetime.now()
        diff_time = time_now - self.session_age

        # 10 minutes session expiry
        if (diff_time.total_seconds() > 600):
            gCon.log("Session expiration")
            self.user_state = EUserState.NOT_LOGGED
            return False

        # I refresh the time
        self.session_age = time_now
        return True



    # Not only the login is valid, but we have also to be root
    def is_logged_root(self):
        if (self.is_login_valid() != True):
            return False
        
        # the logged user must belong to the admins family.
        if (self.uri.family != 'admins'):
            return False

        return True

