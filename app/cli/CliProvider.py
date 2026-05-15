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
# The class that manages the connections.

# the cli provider is a module which gives Adelphos the possibility
# to have bidirectional channels of messages, a.k.a. sockets.

# However we abstract the interface in order to have the possibility
# to transform sockets into simple function calls.

from abc import ABC, abstractmethod

#from app.transport.RouterProvider import RouterProvider

class CliProvider(ABC):


    @abstractmethod
    async def accept(self, websocket):
        pass


