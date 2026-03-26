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


# the API used to enter the application during testing. Not useful elsewhere.

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
from app.dao.FamilyDto import family_dto_create_local
from app.dao.AliasDto import alias_dto_create_local
from app.api.UserSession import active_login

from app.api.BaseApi import BaseApi
from app.api.BaseApi import only_in_debug
from app.api.UserSession import active_login


class TestApi(BaseApi):


    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    @active_login
    @only_in_debug
    async def _hndl_recho(self):
        msg = self.gateway.get_param_safe('msg')
        gCon.log(f"got message {msg}")
        remote_instance = self.gateway.get_param_safe('remote_instance')
        instance_pack = self.gateway.app.dao.ad_instance_dao.\
                get_from_hostname(remote_instance)
        if instance_pack is None:
            raise AdelphosException(None, EAdelhposErrno.ENO_DAEMON_FOR_HOST)
        response = await self.gateway.app.ad_gateway.ad_daemon_api.\
                echo_remote(instance_pack, msg)
        return 'hello world ##alice.tapif@localhost:9911 from localhost:5012' 
        return response


HANDLERS = {
     'test_recho' : TestApi._hndl_recho
}


