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
from app.logging import gCon


class SimpleSocialApiProvider(BaseSocialApiProvider):

    def __init__(self, vhost):
        super().__init__(vhost)


    def get_social_user(self):
        return "test_kernel"


    def _register_rpc_calls(self):

        math_rpcs = MathRPCs.get_rpcs(self) 
        gCon.log(f"The mathrpcs are {math_rpcs}")
        self._add_context_rpcs('math', math_rpcs)


