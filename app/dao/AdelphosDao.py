# the entry point for the database in adelphos_ap.

# the database for now is a simple sqlite database.


#from ..config import get_config
from ..logging import gCon
import os
from pathlib import Path
import sqlite3


class AdelphosDao:


    def _create_schema(self):
        gCon.log("Creating schema...")

        create_schema_sql = """

create table alias(
        id integer primary key,
        name text,
        inbox text,
        password text,
        public_key blob); 

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
    def get_alias_for_actor():
        pass


    # creates the alias for an actor:
    def create_alias():
        pass


    def delete_alias():
        pass


    def update_alias():
        pass
