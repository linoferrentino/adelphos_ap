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
from dataclasses import asdict
from ..logging import gCon

# This is the base class for the DAOs in adelphos: the one which are for alive
# and for inanimate objects and also for the Activity Pub part of the DB
# (not federated)
class BaseDao(ABC):


    def __init__(self, dao):
        self.dao = dao


    # this method has here a default implementation, but we can override it
    def store(self, dto):
        dto_as_dict = asdict(dto)
        new_id = self.store_dict(dto, dto_as_dict)
        return new_id


    # this is the abstract method that derived classes must implement
    @abstractmethod
    def store_dict(self, dto, dto_as_dict):
        pass


