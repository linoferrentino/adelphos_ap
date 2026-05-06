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


    def __init__(self, host, gateway):
        self.host = host
        self.gateway = gateway
        self.in_app = None

        if gateway is not None:
            gateway.register_dns(self, host)


    def get_loop(self):
        if self.gateway is not None:
            return self.gateway.get_loop()
        return 

    
    def post_json(self, url, json):
        pass


    def register_reverse_path(self, in_app):
        self.in_app = in_app


    async def get_json(self, url):
        urls = urlsplit(url)
        if urls.netloc == self.host:
            return self.host.in_get_json(urls)
        #gCon.log(f"get json {url}")
        if self.gateway is None:
            raise Exception(f"Network unavailable. {self.host}")
        val = await self.gateway.route_message("GET", urls)
        return val.body


    def in_get_json(self, urlp):
        if urlp.netloc != self.host:
            raise Exception("Invalid host")
        if self.in_app is None:
            return Response(500, None)
        return self.in_app.in_get_json(urlp)


    #(urls, host) = self._get_routable_host(url)
    #    if host is None:
    #        if self.gateway is None:
    #            raise Exception(f"No route to host {urls.netloc}")
    #    return host.in_get_json(urls)

    #def in_get_json(self, urlp):
    #    assert False

