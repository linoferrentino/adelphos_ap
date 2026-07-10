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
# The DAO relative to the Activity Pub Actor

from urllib.parse import urlparse
from app.logging import gCon
from app.dao.BaseDao import BaseDao
from app.dao.ApActorDto import ApActorDto
from app.dao.ApActorDto import ApActorImpl
from app.dao.ApActorDto import create_remote_actor
from app.ap_api.AsyncRequest import AsyncGetReq
from dataclasses import asdict
import json
#from app.api.AdelphosException import AdelphosException

# this is the class that holds the logic to query and to
# instantiate actor DTOs
# This Dao does not derive from AdelphosObjectDao because
# the actors are not part of the adelphos federated DB
class ApActorDao(BaseDao):

    # I can set here the context.
    def __init__(self, dao):
        super().__init__(dao)

        self.ftbl_col_list = ( "server_fk", 
                              "user_path", "preferred_username",
                              "inbox_path", "private_key", "public_key",
                              "actor_id", "local_fk", "timestamp"
                              )
        self.table_name = "ap_actor"



    def get_from_id(self, actor_id):
        return self.db.get_full_dto_ex(self.table_name, 
                    ("actor_id",), (actor_id,), ApActorImpl)


    # more than one user can have the same preferred_username in different servers.
    def get_from_preferred_username(self, server_fk, preferred_username):
        return self.db.get_full_dto_ex(self.table_name,
            ('server_fk', 'preferred_username'),
            (server_fk, preferred_username), ApActorImpl)


    def get_from_server_path(self, server_fk, user_path):
        return self.db.get_full_dto_ex(self.table_name,
            ('server_fk', 'user_path'),
            (server_fk, user_path), ApActorImpl)


    # this function tries to get an actor from
    # the local db using the hostname and 
    def get_local_from_parsed_uri_XX(self, server_dto, key_parsed):
        # I have to query the view.
        #gCon.log(f"this actor's Activity Pub host is {key_parsed.netloc}")
        #gCon.log(f"his path is  is {key_parsed.path}")

        table_name = "ap_actor"

        fields_to_seek = ('server_fk', 'user_path')
        values_to_seek = ( server_dto.server_id, key_parsed.path)

        dto = self.dao.db.get_full_dto_ex(table_name,  fields_to_seek, 
                            values_to_seek, ApActorDto)
 
        return dto

    
    # this function will get from uri, the actor has been already taken.
    async def get_or_discover_from_uri_XX(self, server_dto, key_parsed):

        parsed = key_parsed._replace(fragment = "")
        actor_uri = parsed.geturl()

        ap_actor_dto = self.get_local_from_parsed_uri(server_dto, key_parsed)

        if (ap_actor_dto is None):
            ap_actor_dto = await self.create_from_uri(server_dto, actor_uri, 
                                                   key_parsed)
        return ap_actor_dto


    def store_dict(self, actor, actor_as_dict):

        table_name = "ap_actor"

        #public_key_save = actor.public_key

        if actor.private_key is not None:
            assert actor.public_key is not None
            #actor.public_key = None
            actor_as_dict['public_key'] = None

        #fields_stored = {
        #                 'server_fk': actor.server_fk,
        #                 'user_path': actor.user_path,
        #                 'preferred_username': actor.preferred_username,
        #                 'inbox_path': actor.inbox_path,
        #                 'private_key': actor.private_key,
        #                 'public_key': actor.public_key,
        #                 }
        fields_stored = ('server_fk', 'user_path', 'inbox_path',
                         'preferred_username', 'private_key', 'public_key')

        gCon.log(f"These are the fields {fields_stored}")

        newid = self.db.insert_dto_fields(table_name, fields_stored, actor_as_dict)

        #actor.public_key = public_key_save
        actor.actor_id = newid
        return newid

    
    # gets the name of the column that stores the private key.
    def get_pk_name(self):
        return 'actor_id'


    # We have a table name for each DAO (at least once)
    def get_table_name(self):
        return 'ap_actor'

