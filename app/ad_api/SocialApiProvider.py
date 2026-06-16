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

    def __init__(self, vhost, social_name):
        super().__init__(vhost)
        self.social_name = social_name
 

    #async def remote_req(self, cmd, host, **kwargs):
    #    pass


    def add_context_listener(self, context, listener):
        pass


    @abstractmethod
    async def remote_req(self, context, cmd, host, **kwargs):
        pass


    @abstractmethod
    def get_social_user(self):
        pass


