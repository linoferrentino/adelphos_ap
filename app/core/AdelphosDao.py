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

# the base abstract class that allows the persistence of
# the objects in adelphos

from abc import ABC, abstractmethod


# this is the local adelphos dao, not federated. All the methods are 
# def not async def. So we do not have the ActivityPub part.
class AdelphosDao(ABC):


    def alias_dao():
        pass

    
    @abstractmethod
    def get_family(self, family):
        pass


    @abstractmethod
    def add_family(self, family):
        pass


