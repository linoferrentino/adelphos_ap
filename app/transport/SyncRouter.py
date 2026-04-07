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


class SyncRouter:


    def __init__(self):
        self.routes = {}


    def _register_route(self, route, action):
        pass


    def get(route, *args):

        return 99


    def post(route, *args):

        # usually this is the normal return code
        return 202
