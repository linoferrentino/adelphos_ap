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


class SocialProvider(ABC):


    @abstractmethod
    def local_user_exists(self, user: str) -> bool:
        pass


    @abstractmethod
    def incoming_message(self, user, message):
        pass


    @abstractmethod
    async def outgoing_message(self, user, message):
        pass


    @abstractmethod
    def create_or_register_user(self, user, *, a_listener = None):
        pass


    #@abstractmethod
    #def login_user(self, user, password):
    #    pass



