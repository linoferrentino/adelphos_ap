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
#


from abc import ABC, abstractmethod

class Routable(ABC):


    def set_transport(self, transport):
        self.transport = transport


    @abstractmethod
    def get_routes(self):
        pass


    @abstractmethod
    async def init_up(self):
        pass


    @abstractmethod
    async def tear_down(self):
        pass



