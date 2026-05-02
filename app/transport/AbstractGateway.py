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

from abc import ABC
from abc import abstractmethod


class AbstractGateway(ABC):


    # <----- Inbound
    # these are NOT routed, they are called by the underlying transport
    #@abstractmethod
    #def in_get_json(self, url_parsed ):
    #    pass


    #@abstractmethod
    #def in_post_json(self, url_parsed, json):
    #    pass


    ## functions to have the sockets.
    #@abstractmethod
    #def accept(self, server_socket):
    #    pass

    @abstractmethod
    def _post_json(self, url_parsed, json):
        pass


    def _get_json(self, url_parsed):
        pass
