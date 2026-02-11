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

class BaseFractalGroupDao(FdActorDao):


    def __init__(self, dao, ftbl_col_list, level_constraint_sql = None):
        self.level_constraint_sql = level_constraint_sql
        super().__init__(dao, "fd_group_family" , ftbl_col_list)


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
        gCon.log(f"This is my query {sql_to_do}")

        row = self.dao.db.execute_and_fetch_one(sql_to_do, (name,))

        gCon.log(f"this is the row {row}")

        return None
                 

    def store_dict(self, dto_as_dict):
        gCon.log("Storing the base fractal group dao")
        new_id = super().store_dict(dto_as_dict)
        gCon.log(f"now storing base Fractal group with id {new_id}")
        return new_id


