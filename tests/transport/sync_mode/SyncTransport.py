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

from app.transport.AbstractTransport import AbstractTransport
from urllib.parse import urlsplit
from app.logging import gCon


class SyncTransport(AbstractTransport):


    def __init__(self, host, in_gw):
        self.host = host
        self.in_app = in_gw 
        self.gateway = None


    def _check_gateway_local(self, url):
        urls = urlsplit(url)
        if urls.netloc == self.host:
            return (True, urls)
        if self.gateway is None:
            raise Exception(f"{id(self)} Network unavailable {self.host}")   
        return (False, urls)


    async def post_json(self, url, json):
        pass


    def set_out_gateway(self, gateway):
        self.gateway = gateway 
        gateway.register_dns(self, self.host)


    async def get_json(self, url):
        (is_local, urls) = self._check_gateway_local(url)
        if is_local == True:
            val = self.in_get_json(self, urls)
        else:
            val = await self.gateway.route_message("GET", urls)
        return val.body


    def in_get_json(self, urlp):
        if urlp.netloc != self.host:
            raise Exception("Invalid host")
        if self.in_app is None:
            return Response(500, None)
        return self.in_app.in_get_json(urlp)



