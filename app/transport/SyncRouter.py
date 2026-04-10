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
# A class that manages the routing table for a synchronous application
# (useful in testing)

from app.transport.AbstractTransport import AbstractTransport
from tests.TestResponse import TestResponse
from urllib.parse import urlsplit

class SyncRouter(AbstractTransport):


    def __init__(self):
        self.routes = {}
        self.host = None
        # the router at first hasn't a gateway
        self.gateway = None


    def _register_post_route(self, route, action):
        pass


    def _register_get_route(self, route, action):
        pass


    def post_json(self, url_str, json):
        return TestResponse(202, None)


    def get_json(self, url_str):

        # parse the url lib.
        parsed_url = urlsplit(url_str)

        if ((parsed_url.netloc is None) or
            (parsed_url.netloc == self.host)):
            return TestResponse(404, None)
        elif self.gateway is None:
            raise Exception("No gateway and not local net {parsed_url.netloc}")
        else:
            return self.gateway.get_json_url(parsed_url)
        



    def accept(self, server_socket):
        pass




