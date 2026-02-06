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

# The base class for all the inanimate objects in adelphos


from dataclasses import dataclass

@dataclass
class FdObjectDto:

    # the name of the object. It is unique in the context of an
    # instance and a type: that is we can have two "foo" objects
    # as long as they are of different types.
    name: str

    # every object in adelphos has a creator, which is an alias.
    creator_fk: int

    # these come from the DB: we have the possibility to assign to them
    # values 
    local_fk: int = None
    timestamp: str = None


