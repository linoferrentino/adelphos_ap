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

# This is the Daemon API, in Activity Pub the daemon answers to
# requests done by other adelphos daemons in the fediverse.


# this is the external daemon api, the one which uses Activity Pub as
# the transport. Inside it there is the normal API which is as if the request
# has been done locally from a web socket.

from app.api.BaseApi import BaseApi

class ApDaemonApi(BaseApi):

    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    # here I can encode a request for the remote adelphos
    def encode_remote_response(self, response):
        pass


    def encode_remote_request(self, response):
        pass


    # this blocks the caller until an answer
    async def make_request(self, remote_instance, request):
        pass


    async def _hndl_daemon_q(self):
        pass


    async def _hndl_daemon_a(self):
        pass



HANDLERS = {
     'daemon_q' : ApDaemonApi._hndl_daemon_q,
     'daemon_a' : ApDaemonApi._hndl_daemon_a,
}

