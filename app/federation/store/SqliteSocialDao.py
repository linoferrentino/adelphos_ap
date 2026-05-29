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

from app.federation.SocialDao import SocialDao
from app.logging import gCon
from app.sdc.Dependencies import Dependencies


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
        public_key text,
        timestamp text default current_timestamp,
        unique (server_fk, user_path) on conflict abort
);"""),

]



class SqliteSocialDao(SocialDao):

    def __init__(self, vhost):
        super().__init__(vhost)


    def srv_get_or_create(self, host_name):
        pass


    def actor_get_local(self, user_name):
        pass


    def actor_store(self, actor_dto):
        pass


    def start_sync(self):

        config = self.vhost.get_dep(Dependencies.CONFIG)
        my_conf = config.get_social_dao_cnf()
        db_name = my_conf['dbname']

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


    def _create_schema(self):

        # I can add the foreign key constraints only without a transaction.
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



