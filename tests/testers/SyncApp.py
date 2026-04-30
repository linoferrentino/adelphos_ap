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


# a sync version of a Starlette application
class SyncApp:


    def __init__(self, routes):
        self.routes = routes


    def in_get_json(self, parsed_url):
        return None


    def in_post_json(self, parsed_url, in_json):
        pass

