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
from app.sdc.Dependency import Dependency
from app.federation.LifespanAware import LifespanAware
from app.federation.SocialListener import SocialListener


class SocialApiProvider(Dependency, LifespanAware, SocialListener):

    def __init__(self, kernel):
        super().__init__(kernel)


    @abstractmethod
    async def remote_req(self, context, cmd, host, **kwargs):
        pass


    @abstractmethod
    def remote_host_allow(self, host):
        pass


    @abstractmethod
    def remote_host_deny(self, host):
        pass


    @abstractmethod
    def get_social_user(self):
        pass


