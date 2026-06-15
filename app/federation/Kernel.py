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
from app.federation.LifespanAware import LifespanAware
from app.sdc.Dependency import Dependency
from app.federation.SocialListener import SocialListener
from app.sdc.Dependencies import Dependencies
from app.logging import gCon


class Kernel(Dependency, LifespanAware, SocialListener):

    def __init__(self, vhost, social_name):
        super().__init__(vhost)
        self.social_name = social_name


    @abstractmethod
    def get_syscalls(self):
        pass


    async def start_async(self):
        gCon.log(f"{id(self)} ============================= START ASYNC")
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        social.add_listener(self.social_name, self)
        gCon.log(f"Registered user {self.social_name}")


    async def stop_async(self):
        gCon.log(f"{id(self)} ============================= STOP ASYNC")
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        social.remove_listener(self.social_name)


