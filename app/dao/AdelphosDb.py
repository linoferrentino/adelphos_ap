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


# the entry point for the database in adelphos_ap.

# the database for now is a simple sqlite database.

from ..logging import gCon
from ..logging import good_bye
import os
from pathlib import Path
import sqlite3

# I import here the specialized DAOs to access the federated objects.

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


# this is the entrance point to the federated database in adelphos.
class AdelphosDb_OO:



    # for testing I can also create the file in memory
    def __init__(self, db_name):

        #config = app.config
        #db_name = config['General']['db_name']

        self.create_schema = False

        if (db_name == ":memory:"):

            #gCon.log("I will use the in-memory database")
            db_name_complete = db_name
            self.create_schema = True
            self.mem_db = True

        else:

            db_name_complete = f"{db_name}.sqlite"

            gCon.log(f"I will use database {db_name_complete}")

            if (os.path.exists(db_name_complete) == False):
                self.create_schema = True

            self.mem_db = False

        # create the connection, autocommit will be False after we
        # set the primary keys
        self._conn = sqlite3.connect(db_name_complete,
                                     autocommit=True)
      
        if (self.create_schema == True):
            self._create_schema()


            # If I am here I have to create also the initial data
            # like the root user and maybe all the initial population
            #app.post_initialization_needed()


    # this has a list of queries, and they are combined
    def get_dto_ex(self, table_name, fields_to_ask, fields_to_seek, 
                values_to_seek, constructor_dto):

        list_sql_fields = ", ".join(fields_to_ask)

        condition_str = self.build_condition_str(fields_to_seek)

        sql_get = f"""
select {list_sql_fields} from {table_name} where {condition_str} 

"""
        cur = self._conn.cursor()
        cur.execute(sql_get, values_to_seek)
        row = cur.fetchone()
        cur.close()

        if (row is None):
            gCon.log(f"No {table_name} with |{condition_str}| \
{values_to_seek}")
            return None

        # I simply get the dto 
        return constructor_dto(*row)


    # executes a query and fetch the first result row.
    def execute_and_fetch_one(self, sql, params):
        cur = self._conn.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        return row


    # gets the first row from the sql with the given constructor, None if no row
    # is present.
    def get_dto_from_sql(self, sql, params, constructor_dto):
        row = self.execute_and_fetch_one(sql, params)
        if (row is None):
            return None
        return constructor_dto(*row)


    # simple debug function
    def dump_table(self, table, limit_rows = -1):

        sql = f"""select * from {table}"""
        if limit_rows != -1:
            sql += f" limit {limit_rows}"
        cur = self._conn.cursor()
        cur.execute(sql)
        i = 0
        while True:
            row = cur.fetchone()
            if row is None:
                break
            gCon.log(f"Row {i} : {row}")
            i += 1
        cur.close()



    def get_dto(self, table_name, fields_to_ask, field_to_seek, 
                value_to_seek, constructor_dto):

        list_sql_fields = ", ".join(fields_to_ask)

        sql_get = f"""
select {list_sql_fields} from {table_name} where {field_to_seek} = ?

"""
        cur = self._conn.cursor()
        cur.execute(sql_get, (value_to_seek,))
        row = cur.fetchone()
        cur.close()

        if (row is None):
            gCon.log(f"No row in {table_name} for {field_to_seek} \
= {value_to_seek}")
            return None

        #gCon.log(f"I have read {row}")

        # I simply get the dto 
        return constructor_dto(*row)


    # A generic function to insert a data object: this will use all the
    # keys inside the dictionary
    def insert_dto(self, table_name, dto_as_dict):
        fields = dto_as_dict.keys()
        return self.insert_dto_fields(table_name, fields, dto_as_dict)



    def update_dto(self, table_name, key_name, key_val, dto_as_dict):
        fields = dto_as_dict.keys()
        self.update_dto_fields(table_name, key_name, key_val,  fields, dto_as_dict)


    
    def update_field(self, table_name, key_name, key_val, field, value):
        fields = (field,)
        values = {
                field : value
                }
        self.update_dto_fields(table_name, key_name,  key_val, fields, values)



    # generic update for a table with a primary key composed of one field
    def update_dto_fields(self, table_name, key_name, key_val, fields, dto_as_dict):

        fields_colon = [ f":{field}" for field in fields ]
        place_holders_list = ", ".join(fields_colon)
        fields_list = ", ".join(fields)

        sql_update = f"""

update {table_name} set ( {fields_list} ) = ( {place_holders_list} ) 
where {key_name} = {key_val};

        """

        #gCon.log(f"The query to update is {sql_update} with dictionary")
        #gCon.log(dto_as_dict)
        cur = self._conn.cursor()
        cur.execute(sql_update, dto_as_dict)
        cur.close()
        

    def close(self):
        #gCon.log("Shut down the database")
        #if (self.mem_db == True):
        #    self.dump_database()
        self._conn.close()


    def commit(self):
        self._conn.commit()


    def rollback(self):
        self._conn.rollback()
