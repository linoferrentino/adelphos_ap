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


from abc import ABC, abstractmethod
from app.ad_api.SocialApiProvider import SocialApiProvider
from app.logging import gCon
from app.cli.CliParser import CliParser
from app.sdc.Dependencies import Dependencies
from app.core.sys.SysCallGateway import SysCallGateway


class BaseSocialApiProvider(SocialApiProvider, SysCallGateway):

    def __init__(self, vhost):
        super().__init__(vhost)


    async def remote_req(self, context, cmd, host, **kwargs):
        pass


    async def start_async(self):
        social_user = self.get_social_user()
        gCon.log(f"{id(self)} ============= START ASYNC with user {social_user}")
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        social.add_listener(social_user, self)
        gCon.log(f"Registered user {social_user}")

        self._add_syscalls('social')

    
    async def stop_async(self):
        gCon.log(f"{id(self)} ============================= STOP ASYNC")
        social_user = self.get_social_user()
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        social.remove_listener(social_user)


    @abstractmethod
    def get_social_user(self):
        pass


    async def new_post(self, actor_from, msg):
        gCon.log(f"got msg from {actor_from} {msg}")
        cp = CliParser(msg)
        gCon.log(f"These are the params {cp}")
