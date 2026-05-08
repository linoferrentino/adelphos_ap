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


import asyncio
from starlette.applications import Starlette
from app.transport.async_mode.AsyncTransport import AsyncTransport


class StarletteWrap(Starlette):


    def __init__(self, routable, lifespan = None):
        transport = AsyncTransport()
        routable.set_transport(transport)
        routes = routable.get_routes()

        super().__init__(routes = routes, lifespan = lifespan)

        self.transport = transport
        self.running = False
        self.cond = asyncio.Condition()  
        self.in_gw = routable


    def get_config(self):
        return self.in_gw.config


    def set_out_gateway(self, gw):
        self.transport.set_gateway(gw)

