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
    def __init__(self, db):
        super().__init__(db, 'fd_currency',
            ('local_fk', 'symbol', 'human_value'))



