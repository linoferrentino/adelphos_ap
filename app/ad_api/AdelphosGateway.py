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
# The daemon gateway, the entry point to Adelphos, usually encapsulated into the
# ActivityPubGateway



from app.api.Gateway import Gateway
from app.ad_api.AdDaemonApi import AdDaemonApi
import base64
from app.logging import gCon
import json


# this is the object which will process the requests that come from
# Activity Pub
class AdelphosGateway(Gateway):


    def __init__(self, app):
        super().__init__(app)

        self.ad_daemon_api = AdDaemonApi(self)


    # the request is encoded in base64
    async def pre_process_request(self, request):
        gCon.log(f"HERE I got req {request}")

        return (202, str(request))


    def parse_request_string(self, command_line):
        #gCon.log(f"[red]HERE I got req {command_line}[/red]")
        payload_str = self._decode_daemon_message(command_line)
        remote_json = json.loads(payload_str)
        gCon.log(f"Got parsed: {remote_json}")


    def _decode_daemon_message(self, daemon_str):
        remote_payload_b = base64.b64decode(daemon_str.encode())
        remote_payload_str = remote_payload_b.decode()
        return remote_payload_str


    def _encode_daemon_message(self, message_str):
        remote_payload = base64.b64encode(message_str.encode())
        remote_payload_str = remote_payload.decode()
        return remote_payload_str


    # the AdelphosGateway has another way to process the command line
    def post_process_msg(self, msg_out):
        msg_proc = self._encode_daemon_message(msg_out)
        return msg_proc


    # this is returned as an activity pub message.
    async def outgress_result(self, payload):
        gCon.log(f"will outgress {payload}")


