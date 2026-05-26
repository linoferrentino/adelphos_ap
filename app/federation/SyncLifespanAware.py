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

class SyncLifespanAware(ABC):

    @abstractmethod
    def start_sync(self):
        pass


    @abstractmethod
    def stop_sync(self):
        pass
