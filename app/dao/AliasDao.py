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
from app.dao.FamilyDto import family_dto_create
from app.dao.AliasDto import alias_dto_create_local


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


    # the alias has two "actors": himself and the family which he belongs to
    def _store_base_cached(self, instance_id, uri):

        # I create here a simple object not linked to activity pub, because
        # it is only a place holder.
        alias_dto = self.create_alias_impl(None, uri.family, instance_id, uri.name, None)
        gCon.log(f"Return alias {alias_dto} in instance {instance_id}")
        return alias_dto


    # this function will simply use the fields and store the rows in db.
    # this function bypasses all checks! Call it only after validating user input
    def create_alias_impl(self, actor_id, family, instance_id, name, password_hashed):

         # let's create the family
        family_dto = family_dto_create(family, instance_id)

        family_id = self.dao.family_dao.store(family_dto)

        # I use the activity pub actor object to link to the alias
        alias_dto = alias_dto_create_local(name,
                   actor_id, family_id, password_hashed)

        #gCon.log(f"Create alias {name} with family {family_id} and ap_actor {actor_id}")

        # OK, let't try to add it to the database
        new_id = self.store(alias_dto)

        # this new id is also the boss of the family!
        family_dto.boss_fk = new_id
        self.dao.family_dao.update_field(family_dto, 'boss_fk', new_id)

        return alias_dto




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


