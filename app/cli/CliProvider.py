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
#from app.federation.SyncLifespanAware import SyncLifespanAware
from app.sdc.Dependency import Dependency


class CliProvider(Dependency):

    def __init__(self, kernel):
        super().__init__(kernel)

    
    @abstractmethod
    async def serve_forever(self, websocket):
        pass


