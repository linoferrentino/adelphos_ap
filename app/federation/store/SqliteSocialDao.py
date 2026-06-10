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

from app.federation.BaseSocialDao import BaseSocialDao
from app.sdc.Dependencies import Dependencies
from app.dao.ApServerDao import ApServerDao
from app.dao.ApActorDao import ApActorDao
from app.logging import gCon


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
        timestamp text default current_timestamp,
        unique (server_fk, user_path) on conflict abort
);"""),

]



class SqliteSocialDao(BaseSocialDao):

    def __init__(self, vhost):
        super().__init__(vhost)


    def srv_get_or_create(self, host_name):
        return self.server_dao.get_or_create_from_host_name(host_name)

   
    def actor_get_from_parsed_url(self, parsed_url):
        gCon.log(f"asking user server {parsed_url.netloc} path {parsed_url.path}")
        server_dto = self.server_dao.get_from_hostname(parsed_url.netloc)
        if server_dto is None:
            return None
        actor_dto = self.actor_dao.get_from_server_path(server_dto.server_id,
                                                        parsed_url.path)
        return actor_dto

 
    def actor_get(self, server, user_name):
        actor_dto = self.actor_dao.get_from_preferred_username(server.server_id,
                                                               user_name)
        gCon.log(f"actor_get returns {actor_dto}")
        return actor_dto

    
    def start_sync(self):

        config = self.vhost.get_dep(Dependencies.CONFIG)
        my_conf = config.get_social_dao_cnf()
        db_name = my_conf['db_name']

        gCon.log(f"start sync sqlite store with dbname {db_name}")

        self.create_schema = False

        if (db_name == ":memory:"):
            db_name_complete = db_name
            self.create_schema = True
            self.mem_db = True
        else:
            db_name_complete = f"{db_name}.sqlite"
            if (os.path.exists(db_name_complete) == False):
                self.create_schema = True
            self.mem_db = False

        self._conn = sqlite3.connect(db_name_complete,
                                     autocommit=True)
      
        if (self.create_schema == True):
            self._create_schema()

        self.server_dao = ApServerDao(self)
        self.actor_dao = ApActorDao(self)


    def actor_store(self, actor_dto):
        gCon.log(f"storing {actor_dto}")
        BaseSocialDao._fill_public_key(actor_dto)
        return self.actor_dao.store(actor_dto)


    def _create_schema(self):

        self._conn.execute("pragma foreign_keys = ON;")

        self._conn.autocommit = False
        cursor = self._conn.cursor()

        for cmd in create_schema_sql:
            cursor.execute(cmd[1])

        self._conn.commit()


    def stop_sync(self):
        if (self.mem_db == True):
            self.dump_database()

        self._conn.close()


    def dump_database(self):
        for line in self._conn.iterdump():
            gCon.log(f"{line}")


    def build_condition_str(self, fields_to_seek):
        condition = []
        for field_to_seek in fields_to_seek:
            condition.append(f" {field_to_seek} = ? ")

        condition_str = " and ". join(condition)
        #gCon.log(f"the condition is {condition_str}")
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
            #gCon.log(f"No row in {table_name} for |{condition_str}| {values_to_seek}")
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
            #gCon.log(f"No row in {table_name} for {field_to_seek} = {value_to_seek}")
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
        gCon.log(f"Insert sql {sql_insert} with dict {dto_as_dict}")
        cur = self._conn.cursor()
        cur.execute(sql_insert, dto_as_dict)
        newid = cur.lastrowid
        cur.close()

        return newid



