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


from app.ad_api.BaseSocialApiProvider import BaseSocialApiProvider
from tests.testers.MathRPCs import MathRPCs
from app.sdc.Dependencies import Dependencies
from app.logging import gCon
import app.misc.utils as misc


class SimpleSocialApiProvider(BaseSocialApiProvider):

    def __init__(self, vhost):
        super().__init__(vhost)


    def get_social_user(self):
        return "test_kernel"


    def _is_allowed_remote_rpc_host(self, host, mode):
        return True
