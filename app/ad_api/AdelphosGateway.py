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


# this is the object which will process the requests that come from
# Activity Pub
class AdelphosGateway(Gateway):


    def __init__(self, app):
        super().__init__(app)

        self.daemon_api = AdDaemonApi(self)


    # the request is encoded in base64
    async def pre_process_request(self, request):

        return (202, str(request))


    # this is returned as an activity pub message.
    async def outgress_result(self, errno, payload):
        pass


