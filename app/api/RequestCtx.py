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
# This class is the context for all the requests come from ActivityPub

from app.api.AppCtx import AppCtx
from app.api.IngressGateway import ActivityPubIngressGateway


#class RequestCtx(AppCtx):
class RequestCtx:


    def __init__(self, app):
        #super().__init__(app)
        #self.request = request

        # this is the entry point for all the requests that come to the daemon
        # by the ActivityPub world.
        self.ingress_gateway = ActivityPubIngressGateway(app)

        # then I have also the OutgressGateway... later.


    async def ingress_do(self, request):

        return await self.ingress_gateway.ingress(request)




