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


class LifespanAware(ABC):


    def __init__(self, vhost):
        self.vhost = vhost


    @abstractmethod
    async def start_async(self):
        pass

    
    @abstractmethod
    async def stop_async(self):
        pass


