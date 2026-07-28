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


from app.federation.SocialListener import SocialListener
from app.misc.WrapInt import WrapInt
from app.logging import gCon

from abc import abstractmethod, ABC
from app.sdc.Dependency import Dependency

class SocialGateway(Dependency):


    def __init__(self, vhost):
        super().__init__(vhost)


    @abstractmethod
    async def in_inbox(self, user, request):
        pass


    @abstractmethod
    async def out_outbox(self, actor_dto, handle, message):
        pass


