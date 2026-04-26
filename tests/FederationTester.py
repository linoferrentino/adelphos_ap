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

# the class that does the sync tester for MULTIPLE adelphos instances.


import contextlib
from app.transport.AbstractTransport import AbstractGateway
from tests.TestResponse import TestResponse
from urllib.parse import urlsplit


class FederationTester(AbstractGateway):

    def __init__(self):

        self.hosts = list()


    @contextlib.contextmanager
    def do_playground(self):

        try:
            yield
        finally:
            pass


    def add_hosts(self, hosts):

        self.hosts.extend(hosts)


    def _get_routable_host(self, url):
        urls = urlsplit(url)
        if urls.scheme != 'https':
            raise Exception(f"invalid scheme {urls.scheme}")

        for host in self.hosts:
            if urls.netloc != host.hostname:
                continue
            return (urls, host)

        raise Exception(f"No route to host {urls.netloc}")


    def post_json(self, url, json):

        (urls, host) = self._get_routable_host(url)
        response = host.post_json(urls, json)
        return response 


    def get_json(self, url):
        return TestResponse(404, None)


