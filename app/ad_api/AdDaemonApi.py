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

# the normal daemon api, encapsulated into an ActivityPub message

from app.api.BaseApi import BaseApi

class AdDaemonApi(BaseApi):


    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    async def _hndl_echo(self):
        pass


    async def _hndl_get_uri(self):
        pass


    @staticmethod
    def _build_request_message(command, param_dict):
        return "remote msg"


    # returns a uri from a remote adelphos
    async def get_uri_remote(self, ad_instance_dto, uri):
        msg = AdDaemonApi._build_request_message('add_get_uri',
                                                 { 'uri' : uri } )

        # then I will pass to the gateway of the application.
        # I have to create the request.
        # this is a request which is blocking!
        await self.gateway.app.ap_gateway.ap_daemon_api.make_request(ad_instance_dto, msg)



    async def echo_remote(self, ad_instance_dto, echomsg):
        pass



HANDLERS = {
     'add_echo' : AdDaemonApi._hndl_echo,
     'add_get_uri' : AdDaemonApi._hndl_get_uri,
}

