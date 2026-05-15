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

class Kernel(ABC):


    @abstractmethod
    async def start_async(self, social):
        pass

    
    @abstractmethod
    async def stop_async(self):
        pass


