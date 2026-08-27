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
from app.sdc.Dependencies import Dependencies
from app.logging import gCon


class AdelphosApiProvider(BaseSocialApiProvider):

    def __init__(self, kernel):
        super().__init__(kernel)


    def get_social_user(self):
        return "adelphos"


    def _is_allowed_remote_rpc_host(self, host, mode):
        social = self.kernel.get_dep(Dependencies.SOCIAL)
        local_user = social.local_user_get(self.get_social_user())
        if local_user.actor_dto.srv.rpc_enabled == True:
            return True
        return False


