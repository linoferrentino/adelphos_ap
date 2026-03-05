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


    # this method has here a default implementation, but we can override it,
    # returns the new id.
    def store(self, dto):
        dto_as_dict = asdict(dto)
        new_id = self.store_dict(dto, dto_as_dict)
        return new_id


    # stores the full object, we have had the id from another source.
    # it deletes the timestamp, because we want the db to create it
    def store_full_no_ts(self, dto):
        dto_as_dict = asdict(dto)
        dto_as_dict.pop('timestamp', None)
        gCon.log(f"Inserting {dto_as_dict}")
        self.dao.db.insert_dto(self.get_table_name(), dto_as_dict)
        return dto.get_pk()


    def update(self, dto):
        dto_as_dict = asdict(dto)
        pk_id = dto.get_pk()
        pk_name = self.get_pk_name()
        self.update_dict(pk_name, pk_id, dto_as_dict)


    # basic implementation
    def update_dict(self, pk_name, pk_id, dto_as_dict):
        self.dao.db.update_dto(self.get_table_name(),
                                      pk_name, pk_id, dto_as_dict)


    # this is the abstract method that derived classes must implement
    @abstractmethod
    def store_dict(self, dto, dto_as_dict):
        pass


    # gets the name of the column that stores the private key.
    @abstractmethod
    def get_pk_name(self):
        pass


    # We have a table name for each DAO (at least once)
    @abstractmethod
    def get_table_name(self):
        pass
