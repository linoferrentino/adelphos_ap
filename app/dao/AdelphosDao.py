# the entry point for the database in adelphos_ap.

# the database for now is a simple sqlite database.


#from ..config import get_config
from ..logging import gCon
import os
from pathlib import Path
import sqlite3
from app.dao.AliasDao import AliasDao


class AdelphosDao:


    def _create_schema(self):
        gCon.log("Creating schema...")

        create_schema_sql = """

create table alias(
        id integer primary key,
        alias text,
        ext_name text,
        inbox text,
        password text,
        public_key blob,
unique (alias) on conflict abort
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

        else:

            db_name_complete = f"{db_name}.sqlite"

            gCon.log(f"I will use database {db_name_complete}")

            if (os.path.exists(db_name_complete) == False):
                create_schema = True

        # create the connection.
        self._conn = sqlite3.connect(db_name_complete, autocommit=False)

        if (create_schema == True):
            self._create_schema()


    # returns an alias for the actor, if there is not one it will
    # return None.
    def get_alias(self, ctx, ext_name: str) -> AliasDao:
        return None


    # creates the alias for an actor:
    def new_alias(ext_name: str) -> AliasDao:
        pass


    def delete_alias():
        pass


    def commit(self):
        self._conn.commit()


    def create_alias(self, ctx):
        create_alias = """
insert into alias(alias, ext_name, inbox, password, public_key)
values (?, ?, ?, ?, ?);
"""

        cur = self._conn.cursor()

        alias = ctx.alias

        cur.execute(create_alias, (alias.alias, alias.ext_name,
                                   alias.inbox, alias.password,
                                   alias.public_key))

        alias.alias_id = cur.lastrowid

        ctx.need_commit = True

        cur.close()
        


    def update_alias():
        pass
