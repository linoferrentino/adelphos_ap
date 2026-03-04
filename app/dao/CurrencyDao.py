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


# This is the DAO for the currency.
from app.dao.AdelphosObjectDao import AdelphosObjectDao


# this class will handle the logic to get and store currency objects.
class CurrencyDao(AdelphosObjectDao):


    # I create myself with the table and the local columns
    def __init__(self, dao):
        super().__init__(dao)


    def store_dict(self, dto_as_dict):
        pass


    # gets the name of the column that stores the private key.
    def get_pk_name(self):
        return 'local_fk'


    # We have a table name for each DAO (at least once)
    def get_table_name(self):
        return 'fd_currency'

