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


import secrets

from datetime import datetime
from enum import IntEnum
from enum import auto
from app.logging import gCon
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno


class EUserState(IntEnum):
    NOT_LOGGED = auto()
    LOGGED_WITHOUT_TOKEN = auto()
    LOGGED_AND_TOKEN = auto()


def active_login(inner_syscall):

    async def check_logged(kernel, session, pars):
        if not session.is_login_valid():
            gCon.log("NO LOGIN")
            raise AdelphosCoreException(ECoreErrno.ENOLOGIN)
        return await inner_syscall(kernel, session, pars)

    return check_logged


class UserSession:

    def __init__(self, kernel):
        self.kernel = kernel
        self.user_state = EUserState.NOT_LOGGED


    def login_start(self, alias, family, actor_dto):
        self.alias = alias
        self.family = family
        self.token = secrets.token_urlsafe()
        self.session_age = datetime.now()
        self.user_state = EUserState.LOGGED_WITHOUT_TOKEN
        return self.token


    def is_logged_root(self):
        if (self.is_login_valid() != True):
            return False
        
        if (self.family != 'admins'):
            return False

        return True


    @property
    def alias_family(self):
        return f"{self.alias}.{self.family}"


    def is_login_valid(self):
        if (self.user_state != EUserState.LOGGED_AND_TOKEN):
            return False

        time_now = datetime.now()
        diff_time = time_now - self.session_age

        if (diff_time.total_seconds() > 600):
            gCon.log("Session expired")
            self.user_state = EUserState.NOT_LOGGED
            return False

        self.session_age = time_now
        return True


    def accept_token(self, token):
        if (self.user_state == EUserState.LOGGED_AND_TOKEN):
            raise AdelphosCoreException(ECoreErrno.ELOGGED, 
                                        f"Alread logged {self.alias}")
        if (self.user_state != EUserState.LOGGED_WITHOUT_TOKEN):
            raise AdelphosCoreException(ECoreErrno.ENOLOGIN, "Please login first.")
        if (self.token != token):
            raise AdelphosCoreException(ECoreErrno.EWRONG_TOKEN)
        self.user_state = EUserState.LOGGED_AND_TOKEN


# the user session stores all the data that is accumulating during the
# conversation with the user.
class UserSession_OLD:


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


    def whoami(self):
        return self.alias_dto.name


    def accept_token(self, token):
        # Am I in the right state?
        if (self.user_state != EUserState.LOGGED_WITHOUT_TOKEN):
            return False
        if (self.token != token):
            return False
        self.user_state = EUserState.LOGGED_AND_TOKEN
        return True


    def force_token(self):
        self.user_state = EUserState.LOGGED_AND_TOKEN


    def post_login_data(self):
        # here
        pass



