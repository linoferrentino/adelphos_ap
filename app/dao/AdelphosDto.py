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
# this is the base class for all the objects in adelphos


from dataclasses import dataclass



# this is an abstract class, this is the base class for all the
# inanimate objects in adelphos
@dataclass
class AdelphosDto:

    # every object in adelphos has the possibility to have a human name
    # the id is like the IP the name is like a DNS name
    # this could be None
    name: str

    # the creator is an alias
    creator_fk: int

    # every object in adelphos has a local id.
    # this is given by the db engine.
    adelphos_id: int = None

    # the timestamp of this object, created.
    time_created: str = None 



