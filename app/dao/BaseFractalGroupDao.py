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
        super().__init__(dao)
        # I store here the list of fields, the list is coherent
        # with BaseGroupDto
        self.ftbl_col_list = ( "parent_group_fk", 
                              "boss_fk", "cashier_fk",
                              "currency_fk", "equity", "level",
                              "local_fk", "timestamp"
                              )
        self.ftbl_clist_exp = ",".join(self.ftbl_col_list)


    # the local family by definition belongs to instance zero and level zero
    # 
    select_local_name = """
    select {self.ftbl_clist_exp} from fd_group_family as fdg, fd_actor as fda

    where 
    (
    (fdg.local_fk = fda.fd_actor_id)
    and
    (fda.name = ?)
    and
    (fda.instance_fk = 0)
    {self.level_constraint_sql}
    )

    """


    # OK; this is a way to query the db on the local name
    def get_from_local_name(self, name):
        sql_to_do = BaseFractalGroupDao.select_local_name.format(self = self)
        gCon.log(f"This is my query {sql_to_do} with name {name}")

        row = self.dao.db.execute_and_fetch_one(sql_to_do, (name,))

        if (row is None):
            return None

        gCon.log(f"this is the row {row}")

        group = BaseGroupDto(*row) 
        
        gCon.log(f"this is the group {group}")

        return group
                 

    # Here it is a simple passby
    def store_dict(self, dto, dto_as_dict):
        new_id = super().store_dict(dto, dto_as_dict)
        return new_id


