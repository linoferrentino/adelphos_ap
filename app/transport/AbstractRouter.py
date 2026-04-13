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

# this is the low level interface used to post and get messages to an external world

from abc import ABC
from abc import abstractmethod


class AbstractRouter(ABC):

    @abstractmethod
    def register_routes(self, routable):
        pass
