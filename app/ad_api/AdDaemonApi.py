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
import base64
import json
from app.dao.AdelphosUri import uriunparse

class AdDaemonApi(BaseApi):


    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    async def _hndl_echo(self):

        pass


    async def _hndl_get_uri(self):
        uri = self.gateway.get_param_safe('uri')
        pass


    @staticmethod
    def _pack_request_message(command, param_dict):
        cmd_json = {
                'cmd' : command,
                'params' : param_dict
                }
        rcmd_str = json.dumps(cmd_json)
        remote_payload = base64.b64encode(rcmd_str.encode())
        remote_payload_str = remote_payload.decode()
        return remote_payload_str


    # this unpacks the request and returns 
    @staticmethod
    def _unpack_request_message(req_str):
        pass


    @staticmethod
    def _get_uri_remote_payload(uri):
        msg = AdDaemonApi._pack_request_message('add_get_uri',
                                                 { 'uri' : uriunparse(uri) } )
        return msg


    @staticmethod
    def _echo_remote_payload(msg):
        msg = AdDaemonApi._pack_request_message('add_echo', { 'msg' : msg } )
        return msg


    # returns a uri from a remote adelphos
    async def get_uri_remote(self, ad_instance_pack, uri):
        msg = AdDaemonApi._get_uri_remote_payload(uri)
        res = await self.gateway.app.ap_gateway.ap_daemon_api.make_request(
                ad_instance_pack, msg)
        return res


    # this is local from the point of view of this instance.
    def get_uri_local(self, uri_str):
        pass


    async def echo_remote(self, ad_instance_pack, echomsg):
        msg = AdDaemonApi._echo_remote_payload(echomsg)
        res = await self.gateway.app.ap_gateway.ap_daemon_api.make_request(
                ad_instance_pack, msg)
        return res


HANDLERS = {
     'add_echo' : AdDaemonApi._hndl_echo,
     'add_get_uri' : AdDaemonApi._hndl_get_uri,
}

