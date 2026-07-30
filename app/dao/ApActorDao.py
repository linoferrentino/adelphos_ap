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


from urllib.parse import urlparse
from app.logging import gCon
from app.dao.BaseDao import BaseDao
from app.dao.ApActorDto import ApActorDto
from app.dao.ApActorDto import ApActorImpl
from app.dao.ApActorDto import create_remote_actor
from app.ap_api.AsyncRequest import AsyncGetReq
from dataclasses import asdict
import json


class ApActorDao(BaseDao):

    def __init__(self, dao):
        super().__init__(dao)

        self.table_name = "ap_actor"


    def get_from_id(self, actor_id):
        return self.db.get_full_dto_ex(self.table_name, 
                    ("actor_id",), (actor_id,), ApActorImpl)


    def get_from_preferred_username(self, server_fk, preferred_username):
        return self.db.get_full_dto_ex(self.table_name,
            ('server_fk', 'preferred_username'),
            (server_fk, preferred_username), ApActorImpl)


    def get_from_server_path(self, server_fk, user_path):
        return self.db.get_full_dto_ex(self.table_name,
            ('server_fk', 'user_path'),
            (server_fk, user_path), ApActorImpl)


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

        if actor.private_key is not None:
            assert actor.public_key is not None
            actor_as_dict['public_key'] = None
            #gCon.log("REMOVING PUBLIC KEY")

        return super().store_dict(actor, actor_as_dict)


    def update_dto_dict(self, key_val, dto_as_dict):
        if dto_as_dict['private_key'] is not None:
            assert dto_as_dict['public_key'] is not None
            dto_as_dict['public_key'] = None
            #gCon.log("REMOVING PUBLIC KEY before update")

        return super().update_dto_dict(key_val, dto_as_dict)

    
    def get_pk_name(self):
        return 'actor_id'


    def get_table_name(self):
        return 'ap_actor'


    def get_table_data_fields(self):

        return ('server_fk', 'user_path', 'inbox_path',
                'preferred_username', 'private_key', 'public_key', 'tag')


