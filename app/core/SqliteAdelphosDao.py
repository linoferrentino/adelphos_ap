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

# the sqlite DAO will store the data in db.

from app.core.AdelphosDao import AdelphosDao
from app.dao.AdelphosDb import AdelphosDb


# this is the dao which is only limited to one instance.
# it does not go to other instances no async interface
class SqliteAdelphosDao(AdelphosDao):


    def __init__(self, db_name):
        self.db = AdelphosDb(db_name)



