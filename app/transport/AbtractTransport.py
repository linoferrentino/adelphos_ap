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


class AbstractTransport(ABC):


    @abstractmethod
    async def post_and_wait(self, user_from, user_to, request):
        pass


    # Passes the message to the extern and returns only the status code.
    @abstractmethod
    async def post_and_go(self, user_from, user_to, message):
        pass


    #@abstractmethod
    #async def post_and_repeat():
    #    pass
