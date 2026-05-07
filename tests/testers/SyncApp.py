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

import re

import asyncio
import threading

from tests.testers.SyncRequest import SyncRequest
from tests.transport.sync_mode.SyncTransport import SyncTransport
from tests.transport.sync_mode.loop import stop_loop, get_loop, run_coro_in_loop
from urllib.parse import parse_qs

from starlette.responses import Response
from app.logging import gCon


# a sync version of a Starlette application
class SyncApp:

    def __init__(self, host, routable, gateway):

        transport = SyncTransport(host, self, gateway)
        routable.set_transport(transport)
        routes = routable.get_routes()

        self.get_routes = []
        self.post_routes = []

        for route in routes:
            if 'GET' in route.methods:
                self.get_routes.append(SyncApp._translate_sync_route(route))
            elif 'POST' in route.methods:
                self.post_routes.append(SyncApp._translate_sync_route(route))
            else:
                raise Exception(f"invalid method in route {route.methods}")


    @staticmethod
    def _translate_sync_route(route):
        path = route.path
        match_path_param = re.search(r"\{(.*)\}", path)
        if match_path_param is None:
            return route
        path_trans = re.sub("{" + match_path_param.group(1) + "}", 
            f"(?P<{match_path_param.group(1)}>[^/]*)", path)
        route.path = path_trans
        return route


    def in_get_json(self, urlp):
        return self._do_sync_req(self.get_routes, urlp)


    def _get_matched_route(self, parsed_url, routes):
        for route in routes:
            #gCon.log(f"I try to match {route.path} with {parsed_url.path}")
            match_route = re.match(route.path, parsed_url.path)
            if match_route is not None:
                return (route, match_route)
        return (None, None)


    def in_post_json(self, parsed_url, in_json):
        return self._do_sync_req(self.post_routes, parsed_url, in_json)


    def _do_sync_req(self, routes, urlp, in_json = None):

        (route, match_route) = self._get_matched_route(urlp, routes)

        if route is None:
            return Response(None, 404)

        dict_params = parse_qs(urlp.query)

        path_params = dict()
        for k,v in match_route.groupdict().items():
            path_params[k] = v

        endpoint = route.endpoint
        request = SyncRequest(dict_params, path_params, in_json)

        res = run_coro_in_loop(endpoint, request)
        return res

