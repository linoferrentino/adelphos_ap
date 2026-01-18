# the entry point for the database in adelphos_ap.

# the database for now is a simple sqlite database.


from ..logging import gCon
from ..logging import good_bye
import os
from pathlib import Path
import sqlite3
from app.api.AdelphosException import AdelphosException



create_schema_sql = [('actor',

"""
-- this is the table that bridges adelphos with activity pub.
-- here the ids are URIs which are unique enforced by ActivityPub
create table actor (
        actor_uri text primary key,
        canonical_name text, 
        inbox_uri text,
        public_key text,
        timestamp text default current_timestamp,
        unique (canonical_name) on conflict abort
) without rowid;"""),
('instance', """
-- this is the table that caches the instances here in adelphos, there is
-- a one to one mapping between an instance and the daemon actor that this
-- instance exposes.
create table instance (
    
    instance_id integer primary key,
    -- some other flags...
    authorized integer

);"""),
('adelphos_ob', """
-- this is the common part for all the objects in adelphos
create table adelphos_ob (
        -- this is a **local** id, used only to join other tables.
        local_id integer primary key,

        remote_id integer,
        instance_fk integer references instance(instance_id),

        adelphos_uri text unique,
        created text default current_timestamp,
        cloned_on text default current_timestamp,
        -- if the object is pinned cannot be garbage collected.
        pinned integer,
        -- an object which has not a reference to its home
        orphaned integer
        -- maybe other flags? permissions, tags, etc.
);"""),
('group_data', """
create table group_data(
        --group_uri text primary key,
        local_fk integer primary key references adelphos_ob(local_id),
        parent_group_fk text references ad_group(local_fk),
        level integer
        --,
        --timestamp text default current_timestamp

) without rowid;"""),
('alias_data', """
create table alias_data(
        local_id integer primary key references adelphos_ob (local_id),
        actor_fk text references actor(actor_uri) on delete restrict,
        alias text,
        password text
        --timestamp text default current_timestamp
); """)]

#curre
#
#
#create table currency(
#        adelphos_uri text primary key,
#        friendly_name text,
#        human_value real,
#        timestamp text default current_timestamp
#) without rowid;
#
#
#create table cheque(
#        adelphos_uri text primary key,
#        amount integer,
#        date_issued text,
#        issuer_uri_fk text,
#        currency_fk text
#        timestamp text default current_timestamp
#) without rowid;
#
#
#create table session(
#        alias_uri text primary key,
#        token text,
#        confirmed integer,
#        timestamp text default current_timestamp
#) without rowid;
#
#
#-- we do not have here the foreign key, because the alias could be remote
#create table trust_line(
#        adelphos_uri text primary key,
#        alias_from text,
#        alias_to text,
#        trust_val real,
#        timestamp text default current_timestamp,
#        unique (alias_from, alias_to) on conflict abort
#) without rowid;
#
#
#"""



class AdelphosDao:

    # the ids in adelphos are in the form
    # ad1.$type.$val@host
    # where type is one of 'alias', 'group', 'cheque', 'trust_line' etc.
    # there are no numeric ids, because the database is distributed.
    # local instances are free to cache local values as numeric

    # every identifier has a $home, which is the host where it has been
    # created and only that server is allowed to modfify it.

    # the distributed db is distributed equally: we do not alter the rows,
    # only the various adelphos' instances have a different set of rows and
    # they share the responsability to update it.

    # the database is consistent


    def _create_schema(self):
        gCon.log("Creating schema...")


        # the schema is an array of statements with a comment
        cursor = self._conn.cursor()

        for cmd in create_schema_sql:
            gCon.log(f"Will create table {cmd[0]}")
            cursor.execute(cmd[1])

        cursor.close()

        self._conn.commit()


    # for testing I can also create the file in memory
    def __init__(self, config):

        db_name = config['General']['db_name']

        create_schema = False

        if (db_name == ":memory:"):

            gCon.log("I will use the in-memory database")
            db_name_complete = db_name
            create_schema = True
            self.mem_db = True

        else:

            db_name_complete = f"{db_name}.sqlite"

            gCon.log(f"I will use database {db_name_complete}")

            if (os.path.exists(db_name_complete) == False):
                create_schema = True

            self.mem_db = False

        # create the connection.
        self._conn = sqlite3.connect(db_name_complete, autocommit=False)

        if (create_schema == True):
            self._create_schema()
            

    def dump_database(self):
        for line in self._conn.iterdump():
            gCon.log(f"{line}")


    def export_to_remote_dto(ctx):
        pass


    def import_from_dao_remote(ctx):
        pass


    # this has a list of queries, and they are combined
    def get_dto_ex(self, table_name, fields_to_ask, fields_to_seek, 
                values_to_seek, constructor_dto):

        condition = []

        list_sql_fields = ", ".join(fields_to_ask)

        for field_to_seek in fields_to_seek:
            condition.append(f" {field_to_seek} = ? ")

        condition_str = " and ". join(condition)

        gCon.log(f"the condition is {condition_str}")

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


    # this is the entry point for the distributed adelphos database,
    # from the uri we can determine the object type and its location.
    # for now every adelphos instance is equal.
    def get_or_import(self, uri):
        pass


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


    def insert_dto(self, ctx, table_name, dto_as_dict):

        fields = dto_as_dict.keys()
        fields_colon = [ f":{field}" for field in fields ]

        fields_list = ", ".join(fields)
        place_holders_list = ", ".join(fields_colon)


        sql_insert = f"""
insert into {table_name} ( {fields_list} ) values ( {place_holders_list} );

"""

        gCon.log(f"executing {sql_insert}")

        cur = self._conn.cursor()
        cur.execute(sql_insert, dto_as_dict)
        cur.close()

        ctx.need_commit = True
        

    def close(self):
        gCon.log("Shut down the database")
        if (self.mem_db == True):
            self.dump_database()
        self._conn.close()


    def commit(self):
        self._conn.commit()


