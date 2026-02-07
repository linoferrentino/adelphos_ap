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


# this is the specialized Dao used for the Family
# the family is part of the living part of adelphos db


# the family is at level zero trust.
# an alias can belong only to one family.
# a family can cross instances, that is it can have a parent in
# another instance and have members in different instances.
class FamilyDao(BaseFractalGroupDao):


    # the level for me is zero, this will be stored in the query.
    def __init__(self, dao):
        super().__init__(dao, ("local_fk",
                "parent_group_fk", "boss_fk", "currency_fk", "equity"),
                " and (fdg.level = 0)")



