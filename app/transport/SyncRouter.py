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

class SyncRouter(AbstractTransport):


    def __init__(self):
        self.routes = {}


    def _register_post_route(self, route, action):
        pass


    def _register_get_route(self, route, action):
        pass


    def post_json(self, url, json):
        return TestResponse(202, None)


    def get_json(self, url):
        return TestResponse(404, None)


    def accept(self, server_socket):
        pass




