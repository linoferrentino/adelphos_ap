# the entry point for the database in adelphos_ap.

# the database for now is a simple sqlite database.


from ..logging import gCon
from ..logging import good_bye
import os
from pathlib import Path
import sqlite3
from app.dao.AliasDto import AliasDto
from app.api.AdelphosException import AdelphosException
from app.dao.CachedActorDto import CachedActorDto


class AdelphosDao:


    def _create_schema(self):
        gCon.log("Creating schema...")

        create_schema_sql = """

-- this is a local table: all the actors can be erased, except
-- the ones who hold a local alias in adelphos.
create table cached_actor (
        actor_id integer primary key,
        preferred_username text,
        hostname text,
        actor_uri text unique on conflict abort,
        inbox_uri text,
        public_key text,
        date_created text default current_timestamp,
        unique (preferred_username, hostname) on conflict abort
);


-- this is a local table, it lists my aliases: other table in
-- adelphos are distributed.
create table alias(
        alias_id integer primary key,
        actor_fk integer references cached_actor(actor_id)
        on delete restrict,
        password text,
        alias text unique on conflict abort,
        date_created text default current_timestamp
        ); 

-- this is a cached trust line, it can be recomputed
create table cached_tl(
    alias_fk integer references alias(alias_id),
    tl_fk integer references trust_line(tl_id)
);


-- this is a distributed table; the same line in different servers could
-- have a different id, but this is not a problem, because the computation
-- does not depend on it.
create table trust_line(
        tl_id integer primary key,
        alias_from integer references alias(alias_id),
        alias_to text,
        trust_val real,
        date_created text default current_timestamp,
        unique (alias_from, alias_to) on conflict abort
);



"""

        cursor = self._conn.cursor()

        cursor.executescript(create_schema_sql)

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
            gCon.log(f"No row in {table_name} with |{condition_str}|")
            return None


        # I simply get the dto 
        return constructor_dto(*row)


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

        new_id = cur.lastrowid
        cur.close()

        ctx.need_commit = True

        return new_id
        

    def close(self):
        gCon.log("Shut down the database")
        if (self.mem_db == True):
            self.dump_database()
        self._conn.close()


    def commit(self):
        self._conn.commit()

    # execs the cursor and close it
    def _exec_cursor_safe(self, ctx, cur, sql, pars):

        try:
            cur.execute(sql, pars)
        except sqlite3.Error as err:
            raise AdelphosException(f"db error {err}")


    def create_alias(self, ctx):

        create_alias = """
insert into alias(alias, ext_name, inbox, password, public_key)
values (?, ?, ?, ?, ?);
"""

        cur = self._conn.cursor()

        alias = ctx.alias

        self._exec_cursor_safe(ctx, cur, 
                    create_alias, (alias.alias, alias.ext_name,
                    alias.inbox, alias.password,
                    alias.public_key))

        alias.alias_id = cur.lastrowid

        ctx.need_commit = True

        cur.close()
        


    def update_alias():
        pass
