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
from urllib.parse import urlparse
from urllib.parse import parse_qs
import re


class SyncRoute:

    def __init__(self, route_rex, action, params):
        self.route_rex = route_rex
        self.action = action
        self.params = params


class SyncRouter(AbstractTransport):


    def __init__(self):
        self.routes = list()
        self.host = None
        # the router at first hasn't a gateway
        self.gateway = None


    def _register_post_route(self, route, action):
        pass


    # I can register a route with a 
    def _register_get_route(self, route_rex, action, *params):
        route = SyncRoute(route_rex, action, params)
        self.routes.append(route)


    def post_json(self, url_str, json):
        return TestResponse(202, None)


    def get_json(self, url_str):

        # parse the url lib.
        parsed_url = urlparse(url_str)

        if ((parsed_url.netloc is None) or
            (parsed_url.netloc == self.host)):

            # I can directly call myself, this is a localhost route
            return self.in_get_json(parsed_url)

        elif self.gateway is None:
            raise Exception("No gateway and not local net {parsed_url.netloc}")
        else:
            return self.gateway.get_json_url(parsed_url)
        

    def in_get_json(self, parsed_url):

        for route in self.routes:
            match_route = re.match(route.route_rex, parsed_url.path)
            if match_route is None:
                continue

            dict_params = parse_qs(parsed_url.query)

            parq = {}
            for param in route.params:
                parq[param] = dict_params[param][0]
            result = route.action(parq)
            return result
        
        # No route!
        return TestResponse(404, None)


    def in_post_json(self, url_parsed, json):
        pass


    def register_routes(self, routable):
        routable.register_sync_routes(self)


    def accept(self, server_socket):
        pass




