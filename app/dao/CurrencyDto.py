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

# this is the currency data class
# A currency in adelphos is linked to a normal currency in the outside
# world, however a user is free to create his own currency, if he likes,
#
# two parties must in any case agree to the currency used, based on
# the trust between them

# *everything* in adelphos is ultimately linked to trust.

from dataclasses import dataclass
from app.dao.AdelphosObjectDao import AdelphosObjectDao


@dataclass
class CurrencyDto:

    # the id is not here, because we always have a 1:1 mapping to
    # currencies and adelphos objects.

    symbol: str

    human_value: float


# this class will handle the logic to get and store currency objects.
class CurrencyDao(AdelphosObjectDao):


    def __init__(self, dao):
        super().__init__(dao, 'fd_currency',
            ('local_fk', 'symbol', 'human_value'))


    def create_schema(self, app, cursor):
        pass


    # the uri here is parsed.
    def get_from_uri(ctx, uri):
        # Of course the uri must be of the right type
        pass


    def get_from_uri_str(uri):
        pass


    def get_or_create_from_uri(uri):
        pass

