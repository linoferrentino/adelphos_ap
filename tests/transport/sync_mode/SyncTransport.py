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


class SyncTransport(AbstractTransport):


    def __init__(self, host, gateway):
        self.host = host
        self.gateway = gateway

        if gateway is not None:
            gateway.register_dns(self, host)

    
    def post_json(self, url, json):
        pass


    def _get_routable_host(self, url):
        urls = urlsplit(url)
        if urls.scheme != 'https':
            raise Exception(f"invalid scheme {urls.scheme}")

        #for host in self.hosts:
        #    if urls.netloc != host.hostname:
        #        continue
        #    return (urls, host)

        #raise Exception(f"No route to host {urls.netloc}")
        if urls.netloc != self.host:
            return (urls, None)

        return (urls, self)


    def get_json(self, url):

        (urls, host) = self._get_routable_host(url)

        if host is None:
            if self.gateway is None:
                raise Exception(f"No route to host {urls.netloc}")

            return self.gateway.route_message("GET", urls)

        return host.in_get_json(urls)



