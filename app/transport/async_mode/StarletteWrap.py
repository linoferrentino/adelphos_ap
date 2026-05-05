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


from starlette.applications import Starlette
import asyncio


class StarletteWrap(Starlette):

    def __init__(self, transport, routes, lifespan = None):
        super().__init__(routes = routes, lifespan = lifespan)

        self.transport = transport
        self.running = False
        self.cond = asyncio.Condition()  

