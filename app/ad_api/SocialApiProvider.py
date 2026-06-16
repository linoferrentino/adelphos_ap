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


class SocialApiProvider(Dependency, LifespanAware):


    async def remote_req(self, cmd, host, **kwargs):
        pass


    def add_context_listener(self, context, listener):
        pass
