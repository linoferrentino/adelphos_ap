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
from app.sdc.Dependency import Dependency
from app.federation.LifespanAware import LifespanAware
from app.federation.SyncLifespanAware import SyncLifespanAware


class SocialProvider(Dependency, SyncLifespanAware):


    def __init__(self, vhost):
        super().__init__(vhost)


    @abstractmethod
    def local_user_get(self, user_name):
        pass

 
    @abstractmethod
    async def incoming_message(self, actor_from, recipient, message):
        pass


    @abstractmethod
    async def outgoing_message(self, local_user, recipient_str, message):
        pass


    @abstractmethod
    async def out_msg_listener_to_actor(self, actor_dto, message):
        pass


    @abstractmethod
    def add_listener(self, user, listener):
        pass


    @abstractmethod
    def remove_listener(self, user):
        pass


    @abstractmethod
    def get_user_tag(self, user):
        pass


    @abstractmethod
    def set_user_tag(self, user, tag):
        pass


    @abstractmethod
    def create_local_user(self, user):
        pass


