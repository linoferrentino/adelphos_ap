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


# the abstract transport has the methods to post and get json from
# the external world.

# concrete classes can be sync or async: the interface is synchronous, however,
# because we shield the complexity


# we can have a sync interface or a async interface.
# the client will adapt to the correct implementation based on the gateway.

# sync gateways will call the sync interface.

class AbstractTransport(ABC):


    # these are routed -----> Outbound
    @abstractmethod
    def post_json(self, url, json):
        pass


    @abstractmethod
    def get_json(self, url):
        pass


    # <----- Inbound
    # these are NOT routed, they are called by the underlying transport


    # functions to have the sockets.
    @abstractmethod
    def accept(self, server_socket):
        pass
    

