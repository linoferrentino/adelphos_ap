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
    select {self.ftbl_col_list} from fd_group_family as fdg, fd_actor as fdo

    where 

    (
    (fdg.name = ?)
    and
    (fdo.instance_fk = 0)

     {self.level_constraint_sql}
    
    )


    """

    #@abstractmethod
    #def _get_level_constraint(self):

    # OK; this is a way to query the db on the local name
    def get_from_local_name(self, name):
        gCon.rule("This is the query!")
        sql_to_do = BaseFractalGroupDao.select_local_name.format(self = self)
        gCon.log(f"This is my query {sql_to_do}")
        return None
                 

    # Instead a group can have different levels


    # this returns the object from a local name
    # trust groups are unique in the same adelphos instance.
    # (instead aliases are unique only in the same family)
    def get_from_local_name(self, local_name):
        pass


