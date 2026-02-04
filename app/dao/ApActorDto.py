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
@dataclass
class ApActorDto:


    # these cannot be NULL
    server_fk: int
    user_path: str
    preferred_username: str
    inbox_path: str
    public_key: str


    # these can be NULL, they are set by the database.
    actor_id: int = None
    timestamp: str = None


# this is the class that holds the data for an actor and a server
# at the same time, it queries the actor_server view. 
@dataclass
class ApActorServerDto:
    actor_id: int = None
    host_name: str = None

    user_path: str = None
    preferred_name: str = None
    inbox_path: str = None
    public_key: str = None
    timestamp: str = None




