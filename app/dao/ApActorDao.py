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
from app.dao.ApActorDto import create_ap_actor
from app.ap_api.AsyncRequest import AsyncGetReq
from dataclasses import asdict
import json
from app.api.AdelphosException import AdelphosException

# this is the class that holds the logic to query and to
# instantiate actor DTOs
# This Dao does not derive from AdelphosObjectDao because
# the actors are not part of the adelphos federated DB
class ApActorDao(BaseDao):

    # I can set here the context.
    def __init__(self, dao):
        super().__init__(dao)

        # the list is coherent with ApActorDto
        self.ftbl_col_list = ( "server_fk", 
                              "user_path", "preferred_username",
                              "inbox_path", "public_key", "actor_id",
                              "local_fk", "timestamp"
                              )
        self.table_name = "ap_actor"


    # this function will fetch the public key of the actor
    async def create_from_uri(self, server_dto, actor_uri, key_parsed):

        #gCon.log(f"Create here a cached actor {actor_uri}")

        res_key = AsyncGetReq(actor_uri)
        await self.dao.app.async_req_wait(res_key)

        if (res_key.status_code != 200):
           raise AdelphosException(f"Could not fetch the public key {res_key.status_code}")

        key_ob_text = res_key.text

        key_ob = json.loads(key_ob_text)

        #gCon.log(f"this is the actor {key_ob}")

        pub_key_ob = key_ob['publicKey']

        pub_key_ob_id = pub_key_ob['id']

        # are they the same?
        if (pub_key_ob_id != key_parsed.geturl()):
            raise AdelphosException(f"Error, got {pub_key_ob_id} key \
exp {actor_uri}")

        # is he the owner?
        owner = pub_key_ob['owner'] 
        if (owner != actor_uri):
            gCon.log(f"This is bad {pub_key_ob}")
            gCon.log(f"Error, {owner} different from {actor_uri}")
            raise AdelphosException("Bad key")

        inbox_uri = key_ob['inbox']
        preferred_username = key_ob['preferredUsername']

        # I parse the inbox.
        inbox_parsed = urlparse(inbox_uri)

        # the inbox and the actor uri should belong to the same server,
        # if not there is a problem
        if (inbox_parsed.netloc != key_parsed.netloc):
            raise AdelphosException(
f"Cannot store actor with {inbox_parsed.netloc} != {key_parsed.netloc}")

        if server_dto.server_id == 0:
            #gCon.log("[red]This is a locally defined actor![/red]")
            actor = self.get_from_server_path(0, key_parsed.path)
        else:
            # OK, now I can create the actor
            actor = create_ap_actor(server_dto.server_id,
                             key_parsed.path,
                             inbox_parsed.path,
                             preferred_username,
                             pub_key_ob['publicKeyPem'])
            self.store(actor)

        # if it is zero it is a locally defined actor, we do not store it
        # because it would violate the db integrity
        #if (server_dto.server_id != 0):
        #else:
        #    local_actor = 
        #gCon.log(f"Created actor {actor}")
        return actor 


    # this method returns the actor from a local id
    def get_from_local_id(self, local_id):
        return self.dao.db.get_full_dto("ap_actor", "actor_id", local_id,
                                        ApActorDto)


    # more than one user can have the same preferred_username in different servers.
    def get_from_preferred_username(self, server_fk, preferred_username):
        return self.db.get_full_dto_ex(self.table_name,
            ('server_fk', 'preferred_username'),
            (server_fk, preferred_username), ApActorDto)


    def get_from_server_path(self, server_fk, user_path):
        return self.dao.db.get_full_dto_ex(self.table_name,
            ('server_fk', 'user_path'),
            (server_fk, user_path), ApActorDto)


    # this function tries to get an actor from
    # the local db using the hostname and 
    def get_local_from_parsed_uri(self, server_dto, key_parsed):
        # I have to query the view.
        #gCon.log(f"this actor's Activity Pub host is {key_parsed.netloc}")
        #gCon.log(f"his path is  is {key_parsed.path}")

        table_name = "ap_actor"

        fields_to_seek = ('server_fk', 'user_path')
        values_to_seek = ( server_dto.server_id, key_parsed.path)

        dto = self.dao.db.get_full_dto_ex(table_name,  fields_to_seek, 
                            values_to_seek, ApActorDto)
        #gCon.log(f"I have grabbed {dto} from db")
 
        return dto

    
    # this function will get from uri, the actor has been already taken.
    async def get_or_discover_from_uri(self, server_dto, key_parsed):

        parsed = key_parsed._replace(fragment = "")
        actor_uri = parsed.geturl()

        ap_actor_dto = self.get_local_from_parsed_uri(server_dto, key_parsed)

        if (ap_actor_dto is None):
            ap_actor_dto = await self.create_from_uri(server_dto, actor_uri, 
                                                   key_parsed)
        return ap_actor_dto


    def store_dict(self, actor, actor_as_dict):

        table_name = "ap_actor"

        fields_stored = {
                         'server_fk': actor.server_fk,
                         'user_path': actor.user_path,
                         'preferred_username': actor.preferred_username,
                         'inbox_path': actor.inbox_path,
                         'public_key': actor.public_key,
                         }

        newid = self.db.insert_dto_fields(table_name, fields_stored, actor_as_dict)
        actor.actor_id = newid
        return newid

    
    # gets the name of the column that stores the private key.
    def get_pk_name(self):
        return 'actor_id'


    # We have a table name for each DAO (at least once)
    def get_table_name(self):
        return 'ap_actor'

