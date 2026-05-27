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


from app.sdc.Dependency import Dependency
from abc import ABC, abstractmethod


class SocialEncoder_NO(ABC):

    
    @abstractmethod
    async def encode_message(self, message):
        pass


    @abstractmethod
    async def decode_message(self, message):
        pass


class SocialNetwork(Dependency):

    def __init__(self, vhost):
        super().__init__(vhost)


    @abstractmethod
    def get_social_routes(self):
        pass


    #@abstractmethod
    #async def post_to_user(self, user, message):
    #    pass


    #@abstractmethod
    #async def discover_user(self, user):
    #    pass


