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


class AsyncTransport(AbstractTransport):


    def __init__(self, loop):
        self.loop = loop


    def post_json(self, url, json):
        pass


    def get_json(self, url):
        pass


    def in_get_json(self, urlp):
        pass


    def register_reverse_path(self, routable):
        pass
