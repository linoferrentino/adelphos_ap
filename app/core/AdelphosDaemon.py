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

from abc import abstractmethod
from app.sdc.Dependency import Dependency

class AdelphosDaemon(Dependency):

    def __init__(self, kernel):
        super().__init__(kernel)


    @abstractmethod
    async def start(self):
        pass


    @abstractmethod
    async def stop(self):
        pass


    @abstractmethod
    async def reload(self):
        pass


