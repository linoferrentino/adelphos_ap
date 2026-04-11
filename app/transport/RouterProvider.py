######################################################
#
# Adelphos AP: the fractal trust network
#
# Activity Pub implementation
#
# © 2025-26 Lino Ferrentino lino.ferrentino@gmail.com
#
# This is free software. Licensed with GPL version 3
#
######################################################
#
# A class that gives the routing table also for a synchronous application
# (useful in testing)


from abc import ABC, abstractmethod


class RouterProvider(ABC):


    @abstractmethod
    def get_async_router(self):
        """ The async router is used to be attached to async transports """
        pass


    @abstractmethod
    def register_sync_routes(self, router):
        """ The sync router must be attached to sync transports """
        pass
