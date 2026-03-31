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

# The DAO for the alias
from app.dao.FdActorDao import FdActorDao
from ..logging import gCon
from app.dao.AliasDto import AliasDto
from app.dao.AliasDto import AliasExDto


# this is the utility class that handles the business logic
# for an alias object.
class AliasDao(FdActorDao):


    def __init__(self, dao):
        super().__init__(dao, "fd_alias_ex", AliasExDto)

        # the columns are in the same order as AliasDto
        self.ftbl_col_list = ('local_fk', 'actor_fk', 'family_fk', 'password')



    # this is a local function, 
    def get_from_name_family_id(self, name, family_id):
        #gCon.log(f"I look for family Id {family_id} and name {name}")
        sql_get_local_name_family = """
        select  * from fd_alias_ex  where 
    (
    (name = ?)
    and
    (family_fk = ?)
    and
    (instance_fk = 0)
    )

        """

        row = self.dao.db.execute_and_fetch_one(sql_get_local_name_family,
                                                (name, family_id))

        #gCon.log(f"I have obtained {row}")
        #if (row is None):
        #    gCon.log("===== fd actor =====")
        #    self.dao.db.dump_table("fd_actor")
        #    
        #    gCon.log("===== fd alias =====")
        #    self.dao.db.dump_table("fd_alias")

        #    gCon.log("===== fd group family =====")
        #    self.dao.db.dump_table("fd_group_family")

        #    gCon.log("===== fd alias ex ==== ")
        #    self.dao.db.dump_table("fd_alias_ex")

        #    return None

        return AliasExDto(*row)



    # here we have to change the fields.
    # also in this case we do the hierarchical insert.
    def store_dict(self, dto, dto_as_dict):

        # first of all I store the base table

        #gCon.log(f"Store alias dict {dto_as_dict}")

        new_id = super().store_dict(dto, dto_as_dict)

        dto_as_dict['local_fk'] = new_id
        dto.local_fk = new_id

        self.dao.db.insert_dto_fields("fd_alias", self.ftbl_col_list, dto_as_dict)
        #gCon.log(f"Created new alias {dto}")


