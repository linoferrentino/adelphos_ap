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


from app.logging import gCon
from dataclasses import dataclass
from app.dao.FdActorDto import FdActorDto

# This is the class which models an alias in adelphos, usually this is a
# real person in the fediverse.


# The alias seems to belong to one group: in reality he belongs to several
# groups, but we list here only the innermost group, because every group
# has only one parent, from the l-zero group we can go up to all levels.


@dataclass
class AliasDto(FdActorDto):

    # we need an init because the FdActorDto has some default values.
    #def __init__(self, name, instance_id, family_id, password):
    #    super().__init__(name, instance_id)
    #    self.family_fk = family_id
    #    self.password = password

    actor_fk: int

    # every alias is linked to a family, a level zero group
    family_fk: int

    # every alias has a password, but we will have a MFA with Mastodon.
    password: str
    

