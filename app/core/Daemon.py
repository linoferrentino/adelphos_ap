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

class Daemon(Dependency):

    def __init__(self, kernel):
        super().__init__(kernel)
        self._is_running = False
        self.cycle_count = 0

    @property
    def cycles(self):
        return self.cycle_count


    @property
    def is_running(self):
        return self._is_running


    async def start(self):
        await self.start_impl()
        self._is_running = True
        self.cycle_count += 1
        
    async def stop(self):
        await self.stop_impl()
        self._is_running = False


    @abstractmethod
    async def start_impl(self):
        pass


    @abstractmethod
    async def stop_impl(self):
        pass


    async def reload(self):
        await self.stop_impl()
        await self.start()


