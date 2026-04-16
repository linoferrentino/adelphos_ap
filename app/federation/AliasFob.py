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

# this is the federated object used to access aliases in the
# federated database.

# The alias is the only object which can exist independently
# from other links, it has a ``native'' reference count of one.

# the alias is the only object which has a ``double'' name,
# the first and last name (the family name)

class AliasFob(FederatedObject):


    def __init__(self, uri):
        pass

