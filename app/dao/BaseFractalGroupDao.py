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
# This is the base class than handles the fractal groups in adelphos

from app.dao.FdActorDao import FdActorDao
from ..logging import gCon
from app.dao.BaseGroupDto import BaseGroupDto


class BaseFractalGroupDao(FdActorDao):


    def __init__(self, dao, level_constraint_sql = None):
        self.level_constraint_sql = level_constraint_sql
        super().__init__(dao, "fd_group_family_ex", BaseFractalGroupDao)


    # the local family by definition belongs to instance zero and level zero
    # 
    select_local_name = """
    select * from fd_group_family_ex 
    where 
    (
    (name = ?)
    and
    (instance_fk = 0)
    {self.level_constraint_sql}
    )

    """


    # OK; this is a way to query the db on the local name
    def get_from_local_name(self, name):
        sql_to_do = BaseFractalGroupDao.select_local_name.format(self = self)
        #gCon.log(f"This is my query {sql_to_do} with name {name}")

        row = self.dao.db.execute_and_fetch_one(sql_to_do, (name,))

        if (row is None):
            return None

        group = BaseGroupDto(*row) 

        return group
                 

    # this works backwards, inserting first the dependant tables
    def store_dict(self, dto, dto_as_dict):
        new_id = super().store_dict(dto, dto_as_dict)
        # final store into the table, I can add the foreign key
        dto_as_dict['local_fk'] = new_id
        self.dao.db.insert_dto_fields("fd_group_family",
                ('local_fk', 'level'), dto_as_dict)

        gCon.log(f"Stored the group family {dto}")
        return new_id


