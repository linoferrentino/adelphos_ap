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


class AdelphosApiProvider(BaseSocialApiProvider):

    def __init__(self, vhost):
        super().__init__(vhost)


    def get_social_user(self):
        return "adelphos"


    def _is_allowed_remote_rpc_host(self, host, mode):
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        user_tag = social.get_user_tag(self.get_social_user())
        if user_tag is None:
            return False
        perms = user_tag.get('perms')
        if perms is None:
            return False
        return True

