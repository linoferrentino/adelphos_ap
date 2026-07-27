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


from abc import ABC
from abc import abstractmethod
from dataclasses import asdict
from ..logging import gCon

class BaseDao(ABC):

    def __init__(self, db):
        self.db = db


    def store(self, dto):
        pk_id = dto.get_pk()
        dto_as_dict = asdict(dto)
        if pk_id is not None:
            #gCon.log(f"Updating...... {dto_as_dict}")
            self.update_dto_dict(pk_id, dto_as_dict)
            return pk_id

        new_id = self.store_dict(dto, dto_as_dict)
        return new_id


    def store_full_no_ts(self, dto):
        dto_as_dict = asdict(dto)
        dto_as_dict.pop('timestamp', None)
        #gCon.log(f"Inserting {dto_as_dict}")
        self.dao.db.insert_dto(self.get_table_name(), dto_as_dict)
        return dto.get_pk()


    def update(self, dto):
        dto_as_dict = asdict(dto)
        pk_id = dto.get_pk()
        pk_name = self.get_pk_name()
        self.update_dict(pk_name, pk_id, dto_as_dict)


    def update_field(self, dto, field, value):
        pk_id = dto.get_pk()
        pk_name = self.get_pk_name()
        tbl = self.get_table_name();
        self.db.update_field(tbl, pk_name, pk_id, field, value)


    def update_dict(self, pk_name, pk_id, dto_as_dict):
        tbl = self.get_table_name();
        gCon.log(f"update {tbl} with  {dto_as_dict} using primary key {pk_name} = {pk_id}")
        self.db.update_dto(tbl, pk_name, pk_id, dto_as_dict)


    def store_dict(self, ob, obdict):

        newid = self.db.insert_dto_fields(self.get_table_name(),
                                          self.get_table_data_fields(), obdict)
        setattr(ob, self.get_pk_name(), newid)
        return newid


    def update_dto_dict(self, key_val, dto_as_dict):
        tbl = self.get_table_name();
        key_name = self.get_pk_name()
        fields = self.get_table_data_fields()
        self.db.update_dto_fields(tbl, key_name, key_val, fields, dto_as_dict)


    @abstractmethod
    def get_pk_name(self):
        pass


    @abstractmethod
    def get_table_name(self):
        pass


    @abstractmethod
    def get_table_data_fields(self):
        pass
