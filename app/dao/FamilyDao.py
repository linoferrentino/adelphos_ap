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
# The DAO relative to the family

from app.dao.BaseFractalGroupDao import BaseFractalGroupDao
from app.logging import gCon

from dataclasses import asdict

# this is the specialized Dao used for the Family
# the family is part of the living part of adelphos db


# the family is at level zero trust.
# an alias can belong only to one family.
# a family can cross instances, that is it can have a parent in
# another instance and have members in different instances.
class FamilyDao(BaseFractalGroupDao):


    # the level for me is zero, this will be stored in the query.
    def __init__(self, dao):
        super().__init__(dao, " and (fdg.level = 0)")


    # this works backwards, inserting first the dependant tables
    def store_dict(self, dto_as_dict):
        gCon.log("Start to store the family dto")
        new_id = super().store_dict(dto_as_dict)
        gCon.log(f"now the family dao with id {new_id}")

        # final store into the table, I can add the foreign key
        dto_as_dict['local_fk'] = new_id
        gCon.log(f"self is now {self}")
        self.dao.db.insert_dto_fields("fd_group_family",
                ('local_fk', 'level'), dto_as_dict)
        return new_id


    # this is the basic store, I start from the base class and then I go up.
    #def store(self, dto):
    #    dto_as_dict = asdict(dto)
    #    gCon.log("Storing the family DAO!")
    #    new_id = self.store_dict(dto_as_dict)
    #    gCon.log(f"The family id is {new_id}")

    #    # final store into the table.
    #    dto_as_dict['local_fk'] = new_id
    #    gCon.log(f"self is now {self}")
    #    self.dao.db.insert_dto_fields("fd_group_family",
    #            ('local_fk', 'level'), dto_as_dict)


    #    return new_id

