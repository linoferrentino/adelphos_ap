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


from app.transport.AbstractGateway import AbstractGateway

from app.logging import gCon

class SyncGateway(AbstractGateway):


    def __init__(self):
        self.hosts = dict()


    def register_dns(self, transport, host):
        assert host not in self.hosts
        self.hosts[host] = transport


    def start(self, app):
        pass


    def stop(self):
        if len(self.hosts) > 0:
            self.hosts = dict()

 
    def route_message(self, method, urlp, json = None, headers = None):

        transport = self.hosts.get(urlp.netloc)
        if transport is None:
            raise Exception(f"No route to host {urlp}")

        match method:
            case 'GET':
                return transport.in_get_json(urlp)
            case 'POST':
                return transport.in_post_json(urlp, json, headers)
            case _:
                raise Exception(f"Undefined method {method}")

