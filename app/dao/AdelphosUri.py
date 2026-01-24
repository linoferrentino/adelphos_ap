######################################################
#
# Adelphos AP: the fractal trust network
#
# Activity Pub implementation
#
# © 2026 Lino Ferrentino
# lino.ferrentino@gmail.com
#
# This is free software. Licensed with GPL version 3
#
######################################################
#

# The class that parses the URIs in adelphos.
# The URIs are used to identify objects in the federated database

from enum import StrEnum


# the format of an adelphos URI is dependent on the type
# for the alias, the URI is simplified as`

# this is the mechanical URI
# $<type>$<local_id>@<host>


# I can query the database with this URI,
# the database is federated, I could see that
# object somewhere else, but usually it is located
# in the adelphos instance that has created it.

# then I have the human URI

# for example an alias is
# ##alias.family@host in human form
# or
# ##$392@host in mechanical form
# 
# the single @ is for a local alias
# alias

# this is a currency
# #cu#euro@www.adelphos.it

# this is a group
# #gr#terrible_cats@www.adelphos.it

# Or with the numeric ID
# #gr#$1818@www.adelphos.it

# a family (a group of level zero)
# #g0#ferrentino@www.adelphos.it

# this is a place
# #pl#stadium_north@www.adelphos.it

# this is an item.
# #ob#used_pc99@www.adelphos.it





# This enumeration will list all the types in the federated database
# with their compact representation (two letters).
class EAdelphosTypes(StrEnum):
    ALIAS_TYPE = 'al'
    CHEQUE_TYPE = 'cq'
    CURRENCY_TYPE = 'cu'
    FAMILY_TYPE = 'fa'
    GROUP_TYPE = 'gr'
    OBJECT_TYPE = 'ob'
    PLACE_TYPE = 'pl'
    TRUST_LINE = 'tl'


# this function will parse an URI in adelphos and return the
# parsed object.
def uriparse(uri):
    pass


class AdelphosUri:

    def __init__(self):
        pass

