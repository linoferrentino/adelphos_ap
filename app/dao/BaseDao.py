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


    # this is the basic initialization: the col_list is the list of columns which
    # are used to store, which can be different from the columns used to retrieve.
    def __init__(self, dao, ftbl, ftbl_col_list):
        self.dao = dao
        self.ftbl = ftbl
        self.ftbl_col_list = ftbl_col_list
        self.ftbl_clist_exp = ",".join(ftbl_col_list)


    # the basic store method in the adelphos database: this is for federated
    # objects.
    # from the point of view of the dao the dto is a simple dictionary.
    # this simplifies all the inserts, but the user must be careful to
    # the order, because there are the foreign key constraints.
    def store(self, dto):
        dto_as_dict = asdict(dto)
        gCon.log(f"I will store {dto_as_dict} on table {self.ftbl}")
        new_id = self.dao.db.insert_dto_fields(self.ftbl, 
                        self.ftbl_col_list, dto_as_dict)
        return new_id

