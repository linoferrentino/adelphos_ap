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


from dataclasses import dataclass
from app.logging import gCon
from app.ap_api.AsyncRequest import AsyncGetReq
from app.api.AdelphosException import AdelphosException
from urllib.parse import urlparse
import json


# this is the base class for the activity pub actors.
# the fields are in the same order as the columns
@dataclass
class ApActorDto:

    actor_id: int
    server_fk: int
    user_path: str
    inbox_path: str
    preferred_username: str
    public_key: str
    timestamp: str


def create_ap_actor(server_fk, user_path, 
                    inbox_path, preferred_username, public_key):
    ap_actor_dto = ApActorDto(None, server_fk, user_path,
                              inbox_path, preferred_username,
                              public_key, None)
    return ap_actor_dto


# now the constructor for the actor, it sets the defaut to
# the fields which are NULL


# this is the class that holds the data for an actor and a server
# at the same time, it queries the actor_server view. 
#@dataclass
#class ApActorServerDto:
#    actor_id: int = None
#    host_name: str = None
#
#    user_path: str = None
#    preferred_name: str = None
#    inbox_path: str = None
#    public_key: str = None
#    timestamp: str = None
#
#
#

