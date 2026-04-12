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

        self.hosts.append(hosts)


    def post_json(self, url, json):
        return TestResponse(202, None)


    def get_json(self, url):
        return TestResponse(404, None)


