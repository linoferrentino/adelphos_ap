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

        

        # the table alias stores only the local aliases,
        # the other aliases are stored with the string "$alias@host"
        create_schema_sql = """

create table remote_instance (
        remote_instance_id integer primary key,
        hostname text unique on conflict abort,
        endpoint text,
        inbox text,
        public_key text,
        date_created text default current_timestamp
);

create table cached_actor (
        actor_id integer primary key,
        preferred_username text,
        ext_name text unique on conflict abort,
        inbox text,
        public_key text,
        date_created text default current_timestamp
);

create table alias(
        alias_id integer primary key,
        actor_fk integer references cached_actor(actor_id) 
        on delete restrict,
        alias text unique on conflict abort,
        password text,
        date_created text default current_timestamp
        ); 

create table trust_line(
        alias_1 text,
        alias_2 text,
        trust_val real,
        primary key(alias_1, alias_2)
) without rowid;

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
