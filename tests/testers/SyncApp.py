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

from tests.testers.SyncGateway import SyncGateway
from tests.testers.SyncRequest import SyncRequest
from tests.transport.sync_mode.SyncTransport import SyncTransport
from app.transport.bridge.loop import stop_loop, get_loop, run_coro_in_loop
from tests.testers.SyncTester import WebSocketSync
from urllib.parse import parse_qs

from starlette.routing import WebSocketRoute
from starlette.responses import Response, PlainTextResponse 
from app.logging import gCon
from app.exc.AdelphosException import AdelphosException 

from contextlib import contextmanager
from app.transport.Routable import Routable


def exception_sync_middleware(func):

    def inner_handler(self, *args):
        try:
            return func(self, *args)
        except AdelphosException as exc:
            response = PlainTextResponse(f"{exc.out_str}: {exc}",
                                status_code = 401)
            return response

    return inner_handler


class SyncApp:

    gateway = None

    def on_startup(self):
        #gCon.log("SyncApp on_startup")
        if SyncApp.gateway is None:
            SyncApp.gateway = SyncGateway()
            SyncApp.gateway.start(self)
        self.set_out_gateway(SyncApp.gateway)
        #gCon.log(f"Hello! start init in loop {self.routable}")
        run_coro_in_loop(self.routable.init_up, ())
        #gCon.log("Hello! start init in loop done")


    def on_teardown(self):
        SyncApp.gateway.stop()
        run_coro_in_loop(self.routable.tear_down, ())


    def __init__(self, host, routable):

        transport = SyncTransport(host, self)
        self.transport = transport
        routable.set_transport(transport)
        routes = routable.get_routes()

        self.routable = routable

        self.get_routes = []
        self.post_routes = []
        self.ws_routes = []

        for route in routes:
            if isinstance(route, WebSocketRoute) == True:
                self.add_web_socket_route(route)
            elif 'GET' in route.methods:
                self.get_routes.append(SyncApp._translate_sync_route(route))
            elif 'POST' in route.methods:
                self.post_routes.append(SyncApp._translate_sync_route(route))
            else:
                raise Exception(f"invalid method in route {route.methods}")


    def set_out_gateway(self, gw):
        self.transport.set_out_gateway(gw)


    def add_web_socket_route(self, route):
        self.ws_routes.append(route)


    @exception_sync_middleware
    def incoming_websocket(self, path, websock):
        for route in self.ws_routes:
            if route.path != path:
                continue
            websock_dup = WebSocketSync(websock)
            #gCon.log(f"incoming sock {id(websock)} produced {id(websock_dup)}")
            websock.pair_sock = websock_dup
            run_coro_in_loop(route.endpoint, (websock_dup,), wait = False)
            #gCon.log(f"returned {id(websock)}")
            return
        return Response(None, 404)


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


    @exception_sync_middleware
    def in_get_json(self, urlp):
        return self._do_sync_req(self.get_routes, urlp)


    def _get_matched_route(self, parsed_url, routes):
        for route in routes:
            match_route = re.match(route.path, parsed_url.path)
            if match_route is not None:
                return (route, match_route)
        return (None, None)


    @exception_sync_middleware
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

        res = run_coro_in_loop(endpoint, (request,))
        return res

