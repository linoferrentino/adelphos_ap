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

from app.transport.AbstractGateway import AbstractGateway

class SyncGateway(AbstractGateway):


    def __init__(self):
        self.hosts = dict()


    def register_dns(self, transport, host):
        self.hosts[host] = transport


    def route_message(self, method, urlp, json = None):

        transport = self.hosts[urlp.netloc]
        if transport is None:
            raise Exception(f"No route to host {urlp.netloc}")

        raise Exception("HELLO")
