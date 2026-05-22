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


# this is the low level interface used to post and get messages to an external world

from abc import ABC, abstractmethod


class AbstractTransport(ABC):


    # these are routed -----> Outbound
    @abstractmethod
    async def post_json(self, url, json):
        pass


    @abstractmethod
    async def get_json(self, url):
        pass


    @abstractmethod
    def in_get_json(self, urlp):
        pass


