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

from app.dao.FdActorDao import FdActorDao


# this is the specialized Dao used for the Family
# the family is NOT an object!
class FamilyDao(FdActorDao):


    def __init__(self, dao):
        super().__init__(dao, "fd_family", ("local_fk",
                "parent_group_fk", "currency_fk", "equity"))


    def create_schema(self, app, cursor):
        # this will create the schema (tables and views)
        pass



