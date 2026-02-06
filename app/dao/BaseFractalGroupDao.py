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

class BaseFractalGroupDao(FdActorDao):


    def __init__(self, dao, ftbl, ftbl_col_list):
        super().__init__(dao, ftbl, ftbl_col_list)


    # the local family by definition belongs to instance zero,
    # 
    select_local = """
    select {ftbl_col_list} from fd_group_family, fd_actor


    where 

    (
    ()
    and
    (fdo.instance_fk = 0)
    and
    (fdg.level = 0)
    )


    """


    # this returns the object from a local name
    # trust groups are unique in the same adelphos instance.
    # (instead aliases are unique only in the same family)
    def get_from_local_name(self, local_name):
        pass


