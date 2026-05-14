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

# this is the local basic store in adelphos.
# We have an implementation in sqlite and in memory,
# but in theory other might follow

from abc import ABC, abstractmethod


# The store is always in a transaction,
# but it is NOT thread safe, there is no concept of conflicts, because
# all the operations are serialized.
class SimpleKvStore(ABC):


    @abstractmethod
    def commit(self):
        pass


    @abstractmethod
    def rollback(self):
        pass


    #@abstractmethod
    #def open(self, conn_string):
    #    pass


    #@abstractmethod
    #def close(self):
    #    pass


    @abstractmethod
    def set(self, key, value):
        pass


    @abstractmethod
    def get(self, key):
        pass


    @abstractmethod
    def get_maybe(self, key):
        pass

    
    @abstractmethod
    def has_key(self, key):
        pass


    @abstractmethod
    def del_key(self, key):
        pass
