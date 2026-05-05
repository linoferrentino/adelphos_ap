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
from app.logging import gCon
from urllib.parse import urlsplit

from app.transport.async_mode.AsyncGateway import AsyncGateway

class AsyncTransport(AbstractTransport):


    def __init__(self):
        pass


    def set_gateway(self, gateway):
        self.gateway = gateway


    def post_json(self, url, json):
        assert False


    def get_json(self, url):
        gCon.log(f"getting json {url}")
        urls = urlsplit(url)
        return self.gateway.route_message("GET", urls)


    def in_get_json(self, urlp):
        gCon.log(f"IN getting json {urlp}")
        assert False


    def register_reverse_path(self, routable):
        assert False
