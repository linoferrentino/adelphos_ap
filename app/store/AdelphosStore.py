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

# this is the basic store in adelphos.
# We have an implementation in sqlite and in memory,
# but in theory other might follow

from abc import ABC, abstractmethod


# the adelphos store is a federated key/value database,
# it is able to fetch values from remote instances using a social
# network (in our case activity pub, but it might be different)


class AdelphosStore(ABC):


    @abstractmethod
    def rollback(self):
        pass


    @abstractmethod
    def close(self):
        pass

    # enumerates the keys with a certain regex calling a callback.
    #def enumerate_keys_regex(self, regex, callback):
    #    pass


    #@abstractmethod
    #def init_needed(self):
    #    pass



