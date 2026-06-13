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
#from app.dao.BaseDto import BaseDto
from typing import NamedTuple
from app.dao.ApServerDto import ApServerDto
from app.dao.ApServerDto import create_ap_server


# this is the base class for the activity pub actors.
# the fields are in the same order as the columns in the db table
@dataclass
class ApActorImpl:
    #class ApActorDto(BaseDto):

    actor_id: int
    server_fk: int
    user_path: str
    inbox_path: str
    preferred_username: str
    private_key: str
    public_key: str
    timestamp: str

    #def get_pk(self):
    #    return self.actor_id


#@dataclass
#class ApActorDto_ex:
#
#    #actor_id: int
#    #server_fk: int
#    server_name: str
#    user_path: str
#    inbox_path: str
#    preferred_username: str
#    private_key: str
#    public_key: str


@dataclass
class ApActorDto:

    srv: ApServerDto

    act: ApActorImpl

    def get_inbox(self):
        return f"https://{self.srv.host_name}{self.act.inbox_path}"

    def get_uri(self):
        return f"https://{self.srv.host_name}{self.act.user_path}"


def create_local_actor(server_host, user_path, 
                    inbox_path, preferred_username, private_key):

    server_dto = create_ap_server(server_host)

    actor_impl = ApActorImpl(None, None, user_path,
                              inbox_path, preferred_username,
                              private_key, None, None)

    actor = ApActorDto(server_dto, actor_impl)
    return actor


def create_remote_actor(server_host, user_path, 
                    inbox_path, preferred_username, public_key):

    server_dto = create_ap_server(server_host)
    actor_impl = ApActorImpl(None, None, user_path,
                              inbox_path, preferred_username,
                              None, public_key, None)
    actor = ApActorDto(server_dto, actor_impl)
    return actor 


