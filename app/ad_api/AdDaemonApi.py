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

import base64
import json

from app.dao.AdelphosUri import uriunparse
from app.logging import gCon
from app.api.BaseApi import BaseApi


class AdDaemonApi(BaseApi):


    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    async def _hndl_echo(self):
        msg = self.gateway.get_param_safe('msg')
        gCon.log(f"remote echo msg {msg}")
        answer = f'hello_remote {msg}'
        return answer


    async def _hndl_get_uri(self):
        uri = self.gateway.get_param_safe('uri')
        gCon.log(f"[red] you want this uri {uri}[/red]")
        # I pass the message to the application, hoping it will suceed
        # not maybe, we want an exception in case of failure
        response = await self.gateway.app.dao.uri_factory_str(uri)

        # I want the uri: but I want to export it, so I null the foreign keys.
        gCon.log(f"[red] got {response} [/red]")
        return response


    def _pack_request_message(self, command, param_dict):
        cmd_json = {
                'cmd' : command,
                'params' : param_dict
                }
        rcmd_str = json.dumps(cmd_json)
        return self.gateway._encode_daemon_message(rcmd_str)


    def _get_uri_remote_payload(self, uri):
        msg = self._pack_request_message('add_get_uri',
                                                 { 'uri' : uriunparse(uri) } )
        return msg


    def _echo_remote_payload(self, msg):
        msg = self._pack_request_message('add_echo', { 'msg' : msg } )
        return msg


    # returns a uri from a remote adelphos
    async def get_uri_remote(self, ad_instance_pack, uri):
        msg = self._get_uri_remote_payload(uri)
        res = await self.gateway.app.ap_gateway.ap_daemon_api.make_request(
                ad_instance_pack, msg)
        return res


    # this is local from the point of view of this instance.
    def get_uri_local(self, uri_str):
        pass


    # this is blocking, it is from client side
    async def echo_remote(self, ad_instance_pack, echomsg):
        msg = self._echo_remote_payload(echomsg)
        (errno, answer) = await self.gateway.app.ap_gateway.ap_daemon_api.make_request(
                ad_instance_pack, msg)
        return (errno, answer)


HANDLERS = {
     'add_echo' : AdDaemonApi._hndl_echo,
     'add_get_uri' : AdDaemonApi._hndl_get_uri,
}

