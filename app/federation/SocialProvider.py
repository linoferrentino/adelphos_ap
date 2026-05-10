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

# the social provider is the abstract class used to model a system
# that is able to register users, login them and send to them message
# adelphos is agnostic regarding it.

# For now we rely on ActivityPub and Mastodon, but it could be changed

# We also rely on ActivityPub to exchange messages to remote adelphos,
# in this case we post a message and wait the answer

from abc import ABC, abstractmethod

from app.transport.RouterProvider import RouterProvider

#class SocialProvider(RouterProvider):
class SocialProvider(ABC):

    
    #def __init__(self, transport):
    #    self.transport = transport
    #    pass


    #@abstractmethod
    #def create_user(self, username, is_daemon, listener):
    #    pass

    
    #@abstractmethod
    #def create_or_register_user(self, username):
    #    pass


    @abstractmethod
    def get_user_handle(self, user: str) -> int:
        pass


    @abstractmethod
    def local_user_exists(self, user: str) -> bool:
        pass


    #@abstractmethod
    #async def discover_user(self, username, maybe = False):
    #    pass


    #def discover_user_sync(self, username):
    #    pass


    #def register_listener(self, listener):
    #    self.listener = listener


    @abstractmethod
    def post_message(self, user_handle, message):
        pass



