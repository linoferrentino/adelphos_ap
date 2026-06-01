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
# The DTOs relative to the Activity Pub Actor

import json

from dataclasses import dataclass
from app.logging import gCon
from app.ap_api.AsyncRequest import AsyncGetReq
#from app.api.AdelphosException import AdelphosException
from urllib.parse import urlparse
from app.dao.BaseDto import BaseDto
from typing import NamedTuple
#from app.dao.ApServerDto import ApServerPack


# this is the base class for the activity pub actors.
# the fields are in the same order as the columns in the db table
@dataclass
class ApActorDto(BaseDto):

    actor_id: int
    server_fk: int
    user_path: str
    inbox_path: str
    preferred_username: str
    key: str
    timestamp: str
    public_key: str

    def get_pk(self):
        return self.actor_id


#class ApActorPack_remove(NamedTuple):
#
#    server: ApServerPack
#
#    ob: ApActorDto
#

def create_ap_actor(server_fk, user_path, 
                    inbox_path, preferred_username, key):
    ap_actor_dto = ApActorDto(None, server_fk, user_path,
                              inbox_path, preferred_username,
                              key, None, None)
    return ap_actor_dto


