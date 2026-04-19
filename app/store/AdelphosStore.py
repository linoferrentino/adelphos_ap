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


class AdelphosStore(ABC):


    @abstractmethod
    def commit(self):
        pass


    @abstractmethod
    def rollback(self):
        pass


    @abstractmethod
    def close(self):
        pass


