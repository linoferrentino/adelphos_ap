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

class SocialProvider(ABC):

    
    def __init__(self):

        self.listener = None


    # this methods are called by the fixtures and application to set a test

    # this returns an id, the integer of the newly created user.
    @abstractmethod
    def create_user(self, username):
        pass


    def register_listener(self, listener):

        self.listener = listener


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


