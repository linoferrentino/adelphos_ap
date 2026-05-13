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

from abc import ABC
from abc import abstractmethod


class AbstractGateway(ABC):


    @abstractmethod
    async def start(self, app):
        pass


    @abstractmethod
    async def stop(self):
        pass

 
    @abstractmethod
    async def route_message(self, method, url_parsed, json = None):
        pass


