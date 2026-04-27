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

from app.federation.SocialGateway import SocialGateway

DBSOCIAL_NAME = "AD_DB_D"


def ensure_gw(func):

    def _ensure_gw_present(self, uri):
        if self.gw is None:
            raise Exception("No gateway")
        return func(self, uri)

    return _ensure_gw_present


class FederatedStoreApi:


    def __init__(self, social):

        if social is not None:
            self.gw = SocialGateway(social, DBSOCIAL_NAME)
        else:
            self.gw = None


    @ensure_gw
    def read_uri_no_lock(self, uri):


        pass


    @ensure_gw
    def read_uri_lock(self, uri):
        pass


    @ensure_gw
    def reclaim_locked_uri(self, uri):
        pass
