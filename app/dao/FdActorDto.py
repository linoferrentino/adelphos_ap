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
from app.dao.BaseDto import BaseDto

# here we have all the DTOs relative to the federated actor

# every dataclass is used as a IN or an OUT class, the difference
# is that the OUT class has values for the fields which are written by the DB


# this class is in a certain sense abstract: you do not instantiate directly
# a FdActorDto, but for convenience it is stored in the DB.
@dataclass
class FdActorDto(BaseDto):

    # these are handled by the DB, so I put there.
    # this primary key is relative to the "whole" object.
    fd_actor_id: int 

    # the name of this actor (in case of the alias it is composed of two objects),
    # name and the family's name
    name: str

    # the (adelphos!) instance from which this federated actor comes
    instance_fk: int

    # this is set by the db engine.
    timestamp: str 

    def get_pk(self):
        return self.fd_actor_id


