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


class SocialEncoder(ABC):

    
    @abstractmethod
    async def encode_message(self, message):
        pass


    @abstractmethod
    async def decode_message(self, message):
        pass


class SocialNetwork(ABC):


    def __init__(self, router):
        self.router = router


    @abstractmethod
    def get_social_routes(self):
        pass


    @abstractmethod
    async def post_to_user(self, user, message):
        pass


    @abstractmethod
    async def discover_user(self, user):
        pass


    #def discover_user(self, user):
    #    pass


    #def verify_message(self, user, message):
    #    pass


    #def decode_message(self, user, message):
    #    pass




