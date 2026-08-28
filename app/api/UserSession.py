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
from app.exc.AdelphosException import AdErrno
from app.exc.AdelphosException import AdelphosException
from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType



class EUserState(IntEnum):
    NOT_LOGGED = auto()
    LOGGED_WITHOUT_TOKEN = auto()
    LOGGED_AND_TOKEN = auto()


def active_login(inner_syscall):

    async def check_logged(kernel, session, pars):
        if not session.is_login_valid():
            raise AdelphosException(AdErrno.ENOLOGIN)
        return await inner_syscall(kernel, session, pars)

    return check_logged


class UserSession:

    def __init__(self, client):
        self.client = client
        self.user_state = EUserState.NOT_LOGGED


    def login_start(self, alias, family, actor_dto, alias_ob, force = False):
        self.alias = alias
        self.family = family
        self.token = secrets.token_urlsafe()
        self.session_age = datetime.now()
        if force == False:
            self.user_state = EUserState.LOGGED_WITHOUT_TOKEN
        else:
            self.user_state = EUserState.LOGGED_AND_TOKEN
        self.actor_dto = actor_dto
        self.alias_ob = alias_ob
        return self.token

    
    def get_alias_ob(self):
        return self.alias_ob


    def logout(self):
        self.user_state = EUserState.NOT_LOGGED


    def is_logged_root(self):
        if (self.is_login_valid() != True):
            return False
        
        if (self.family != 'admins'):
            return False

        return True


    @property
    def alias_family(self):
        return f"{self.alias}.{self.family}"


    @property
    def alias_uri(self):
        return AdelphosUri.alias_as_uri(self.alias, self.family, 
            self.client.kernel.conf().get_host())


    @property
    def family_uri(self):
        return AdelphosUri(EAdelphosType.FAMILY_TYPE, self.family,
            host = self.client.kernel.conf().get_host())


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
            raise AdelphosException(AdErrno.ELOGGED, 
                                        f"Alread logged {self.alias}")
        if (self.user_state != EUserState.LOGGED_WITHOUT_TOKEN):
            raise AdelphosException(AdErrno.ENOLOGIN, "Please login first.")
        if (self.token != token):
            raise AdelphosException(AdErrno.EWRONG_TOKEN)
        self.user_state = EUserState.LOGGED_AND_TOKEN



