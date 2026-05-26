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
from app.federation.SyncLifespanAware import SyncLifespanAware


class CliProvider(SyncLifespanAware):

    def __init__(self, kernel):
        self.kernel = kernel

    
    @abstractmethod
    async def serve_forever(self, websocket):
        pass


