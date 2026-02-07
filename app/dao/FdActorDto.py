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

# This is the Federated Actor Dto, the base data class
# for the federated actor.

from app.logging import gCon
from dataclasses import dataclass
from dataclasses import field

# here we have all the DTOs relative to the federated actor

@dataclass
class FdActorDto:

    name: str

    # the (adelphos!) instance from which this federated actor comes
    instance_fk: int

    # these are handled by the DB, so I put there.
    fd_actor_id: int = field(default = None, init = False) 

    timestamp: str = field(default = None, init = False)


# this DTO is used when we create a new actor, some fields have
# default values
@dataclass
class FdActorDtoNew:

    name: str

    # the (adelphos!) instance from which this federated actor comes
    instance_fk: int

    # these are handled by the DB
    fd_actor_id: int = None
    timestamp: str = None



