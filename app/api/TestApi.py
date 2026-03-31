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
        remote_instance = self.gateway.get_param_safe('remote_instance')
        instance_pack = self.gateway.app.dao.ad_instance_dao.\
                get_from_hostname(remote_instance, False)
        response = await self.gateway.app.ad_gateway.ad_daemon_api.\
                echo_remote(instance_pack, msg)
        return response


    @active_login
    @only_in_debug
    async def _hndl_geturi(self):
        uri = self.gateway.get_param_safe('uri')
        no_route  = self.gateway.get_bool_param_safe('no_route', False)

        # the uri has all the information required to get it.
        # the db is federated, so it is possible that also other
        # servers will have the object, if the information is not
        # found we might ask other servers as well.

        # remember that we are here in the local machine!
        # first of all we parse it.
        urip = uriparse(uri)
        response = await self.gateway.app.dao.uri_factory(urip, no_route)
        gCon.log(f"[yellow]Got response {response}[/yellow] no_route {no_route}")
        if response is None:
            raise AdelphosException("Not found", EAdelhposErrno.EREMOTE_URI_NOT_PRESENT)
        return EAdelhposErrno.DONE_OK


HANDLERS = {
     'test_recho' : TestApi._hndl_recho,
     'test_geturi' : TestApi._hndl_geturi,
}


