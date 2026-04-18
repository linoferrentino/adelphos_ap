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

# the social provider needs a transport and itself is a RouterProvider
class SocialProvider(RouterProvider):

    
    def __init__(self, transport):

        self.transport = transport
        pass


    # this methods are called by the fixtures and application to set a test

    # this returns an id, the integer of the newly created user.
    # this creates a user which listens to messages.
    @abstractmethod
    def create_user(self, username, is_daemon):
        pass


    @abstractmethod
    # this does not create the user, but it searches it in the social network
    async def discover_user(self, username, maybe = False):
        pass


    # this will create a demo user with no password in the social.
    # it returns the handle of this user.
    #@abstractmethod
    #def create_human_user(self, username):
    #    pass


    def register_listener(self, listener):
        self.listener = listener


    # this will retry to pass the message until it succeeds
    def post_message(self, userid, message):
        pass


    # returns the last n messages, they are erased in the inbox, by default
    # all are popped.
    #@abstractmethod
    #def pop_last_messages(self, user_id, how_many = -1):
    #    pass


    ## just peeks the last message, it does not erase it.
    #@abstractmethod
    #def peek_last_message(self, user_id):
    #    pass


    ## these are the method called by Adelphos

    ## this does not wait an answer.
    #@abstractmethod
    #def post_user(self, user_id, message):
    #    pass


    ## this waits an answer, from the point of view of Adelphos this
    ## is blocking.
    #@abstractmethod
    #def q_and_a_user(self, user_id, question):
    #    pass


