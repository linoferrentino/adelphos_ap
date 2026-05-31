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


from app.sdc.Dependencies import Dependencies
from abc import ABC, abstractmethod
from app.federation.SocialProvider import SocialProvider
from app.logging import gCon


class BaseSocial(SocialProvider):

    def __init__(self, vhost):
        super().__init__(vhost)


    @abstractmethod
    def create_users(self, server, users):
        pass


    def create_if_not_exists(self, user, *, listener = None):
        pass


    def start_sync(self):
        config = self.vhost.get_dep(Dependencies.CONFIG)
        social_dao = self.vhost.get_dep(Dependencies.SOCIAL_DAO)
        soc_cnf  = config.get_social_config()
        host = config.get_host()
        gCon.log(f"This is the conf {soc_cnf} for host {host}")

        server_dto = social_dao.srv_get_or_create(host)
        gCon.log(f"This is the host {server_dto}")

        users = soc_cnf['users']
        self.create_users(server_dto, users)


