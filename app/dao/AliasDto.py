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

    # this is the Activity Pub actor linked to this alias
    actor_fk: int

    # every alias is linked to a family, a level zero group
    family_fk: int

    # every alias has a password, but we will have a 2FA with Mastodon.
    password: str
    
    # the foreign key towards the fd_actor
    local_fk: int = None

