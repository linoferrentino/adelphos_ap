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

import sqlite3
import os

from app.federation.BaseSocialDao import BaseSocialDao
from app.sdc.Dependencies import Dependencies
from app.dao.ApServerDao import ApServerDao
from app.dao.ApActorDao import ApActorDao
from app.dao.ApActorDto import ApActorDto
from app.dao.ApActorDto import ApActorImpl
from app.logging import gCon
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno


create_schema_sql = \
[
        
('activity_pub_server',
"""
create table ap_server (
    server_id integer primary key,
    host_name text not null unique on conflict abort,
    timestamp text default current_timestamp
);

"""),


('activity pub actor',

"""
create table ap_actor (
        actor_id integer primary key,
        server_fk integer references ap_server(server_id),
        user_path text,
        inbox_path text,
        preferred_username text,
        private_key text,
        public_key text,
        tag text,
        timestamp text default current_timestamp,
        unique (server_fk, user_path) on conflict abort
);"""),

]



class SqliteSocialDao(BaseSocialDao):

    def __init__(self, kernel):
        super().__init__(kernel)


    def _srv_get_or_create(self, host_name):
        return self.server_dao.get_or_create_from_host_name(host_name)

   
    def actor_get_from_parsed_url(self, parsed_url):
        server_dto = self.server_dao.get_from_hostname(parsed_url.netloc)
        if server_dto is None:
            return None
        actor_impl = self.actor_dao.get_from_server_path(server_dto.server_id,
                                                        parsed_url.path)
        if actor_impl is None:
            return None
        actor_dto = ApActorDto(server_dto, actor_impl)
        BaseSocialDao._fill_public_key(actor_dto)
        return actor_dto


    def actor_get_from_id(self, actor_id, maybe = False):
        actor_dto = self.actor_get_from_id_try(actor_id)
        if actor_dto is not None:
            return actor_dto
        if maybe == True:
            return None 
        raise AdelphosCoreException(ECoreErrno.EINVALID_USER_OR_PASSWORD,
                                    f"{actor_id} actor_id not found")


    def actor_get_from_id_try(self, actor_id):
        actor_impl = self.actor_dao.get_from_id(actor_id)
        if actor_impl is None:
            return None
        server_dto = self.server_dao.get_from_id(actor_impl.server_fk)
        assert server_dto is not None
        actor_dto = ApActorDto(server_dto, actor_impl)
        BaseSocialDao._fill_public_key(actor_dto)
        return actor_dto

 
    def actor_get(self, server, user_name):
        server_dto = self.server_dao.get_from_hostname(server)
        if server_dto is None:
            return None
        actor_impl = self.actor_dao.get_from_preferred_username(server_dto.server_id,
                                                               user_name)
        if actor_impl is None:
            return None
        actor_dto = ApActorDto(server_dto, actor_impl)
        BaseSocialDao._fill_public_key(actor_dto)
        return actor_dto

    
    def start_sync(self):

        my_conf = self.conf.get_social_dao_cnf()
        db_name = my_conf['db_name']


        self.create_schema = False

        if (db_name == ":memory:"):
            db_name_complete = db_name
            self.create_schema = True
            self.mem_db = True
        else:
            db_name_complete = db_name
            if (os.path.exists(db_name_complete) == False):
                self.create_schema = True
            self.mem_db = False

        gCon.log(f"[green]Start social database {db_name_complete} [/green]")
        self._conn = sqlite3.connect(db_name_complete,
                                     autocommit=True)
      
        if (self.create_schema == True):
            self._create_schema()

        self.server_dao = ApServerDao(self)
        self.actor_dao = ApActorDao(self)


    def _store_actor_impl(self, actor_dto):
        new_id = self.actor_dao.store(actor_dto.act)
        return new_id


    def _create_schema(self):

        self._conn.execute("pragma foreign_keys = ON;")

        self._conn.autocommit = False
        cursor = self._conn.cursor()

        for cmd in create_schema_sql:
            cursor.execute(cmd[1])

        self._conn.commit()


    def stop_sync(self):
        self._conn.close()


    def dump_database(self):
        for line in self._conn.iterdump():
            gCon.log(f"{line}")


    def build_condition_str(self, fields_to_seek):
        condition = []
        for field_to_seek in fields_to_seek:
            condition.append(f" {field_to_seek} = ? ")

        condition_str = " and ". join(condition)
        return condition_str


    def get_full_dto_ex(self, table_name, fields_to_seek, 
                values_to_seek, constructor_dto):
        condition_str = self.build_condition_str(fields_to_seek)
        sql_get = f"""
select * from {table_name} where {condition_str}

"""
        cur = self._conn.cursor()
        cur.execute(sql_get, values_to_seek)
        row = cur.fetchone()
        cur.close()

        if (row is None):
            return None

        return constructor_dto(*row)



    def get_full_dto(self, table_name, field_to_seek, 
                value_to_seek, constructor_dto):

        sql_get = f"""
select * from {table_name} where {field_to_seek} = ?

"""
        cur = self._conn.cursor()
        cur.execute(sql_get, (value_to_seek,))
        row = cur.fetchone()
        cur.close()

        if (row is None):
            return None

        return constructor_dto(*row)


    # this method will insert only the advertised fields in the db.
    def insert_dto_fields(self, table_name, fields, dto_as_dict):

        fields_colon = [ f":{field}" for field in fields ]

        fields_list = ", ".join(fields)
        place_holders_list = ", ".join(fields_colon)

        sql_insert = f"""
insert into {table_name} ( {fields_list} ) values ( {place_holders_list} );

        """
        cur = self._conn.cursor()
        #gCon.log(f"INSERT {sql_insert} {dto_as_dict}")
        cur.execute(sql_insert, dto_as_dict)
        newid = cur.lastrowid
        cur.close()

        return newid



