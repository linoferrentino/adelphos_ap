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

# the entry point for the database in adelphos_ap.

# the database for now is a simple sqlite database.


from ..logging import gCon
from ..logging import good_bye
import os
from pathlib import Path
import sqlite3
from app.api.AdelphosException import AdelphosException
from app.dao.CurrencyDto import CurrencyDao

# I import here the specialized DAOs to access the federated objects.



create_schema_sql = \
[
        
# the actor zero is the local actor, it corresponds to the local adelphos
# instance.

('actor',

"""
create table actor (
        actor_id integer primary key,
        actor_uri text not null unique on conflict abort,
        canonical_name text not null unique on conflict abort, 
        inbox_uri text,
        public_key text,
        timestamp text default current_timestamp
);"""),

# this is the table that stores the adelphos instances. There
# are not activity pub instances.

('instance', """
create table instance (
    
    instance_id,
    actor_fk integer primary key references actor(actor_id),
    comment text

);"""),


# I create the local instance, this has index zero.
# this holds data for the object in the local host.
# for the other instances I store here the federated daemon endpoint
# this is the only hard coded value in the DB.
# instance zero is the local instance.
# From this identity we can infer if an object is local or not
(
    'create_instance', """insert into instance(instance_id, actor_fk,
    comment, , authorized)
    values(0, NULL, "local adelphos instance");"""
),


# every object in adelphos (apart from the aliases) has a creator who
# is an alias. The alias has a creator who is an actor.
# The alias is the bridge between the world of adelphos and the
# the world of Activity Pub
('adelphos_ob', """
create table adelphos_ob (

        adelphos_id integer primary key,
        creator integer references adelphos_ob(adelphos_id),
        name text,
        instance_fk integer references instance(instance_id),
        created_on text default current_timestamp


);""") ,

# a group has only one parent, like a file system. We do not support
# a mesh like ripple, even if a ripple can be created by following
# the trust lines.

# a person can be thought as a level zero, even if we do have
# different levels.

('group_data', """
create table group_data(

        local_fk integer primary key references adelphos_ob(local_id),

        boss_fk integer references alias_data(local_fk),

        cashier_fk integer references alias_data(local_fk),

        parent_group_fk integer references group_data(local_fk),

        equity real,

        level integer

);"""),


('currency_data', """
create table currency_data(

        local_fk integer primary key references adelphos_ob(local_id),

        symbol text,

        human_value real


);"""),



# the family is the basic group in adelphos
# the level is zero implicit.


('family_data', """
create table family_data(

        local_fk integer primary key references adelphos_ob(local_id),

        parent_group_fk text references ad_group(local_fk),

        currency_fk integer references currency_data(local_fk),

        equity real


);"""),


('view family_raw', """
create view family_raw as select adelphos_id, name, instance_fk, created_on,
 pinned, orphaned, parent_group_fk, currency_fk, equity from
 family_data, adelphos_ob where
 ( (family_data.local_fk = adelphos_ob.adelphos_id) and
   (adelphos_ob.instance_fk = 0) );
"""),




('view family_local', """
create view family_local as select adelphos_id, name, created_on,
 pinned, orphaned, parent_group_fk, currency_fk, equity from
 family_data, adelphos_ob where
 ( (family_data.local_fk = adelphos_ob.adelphos_id) and
   (adelphos_ob.instance_fk = 0) );

"""),


# why do I need to have the alias in another pc? It is a federated
# database, so I need...

# let's do an example, create a trust line.
# I need to create the object @tl$838@www.adelphos.it
# this object stays local in my instance, but needs to be
# used also by the other instance.
# some objects are shared, but they maintain the origin where
# they have been created.


# the alias is the only table which is NOT shared, because we do
# not allow the alias to move (we might), there could be a message
# to allow the moving of the object.



# the table for the alias, this table has a foreign key to the
# adelphos object.

# 1, 'http:///....', linus, pass
# example of a remote alias 

# 
# 32, 'http:///....', john, pass
# and in adelphos object
# 32, 2, NULL, Jan 19th
# this means that the user john
# and in instance
# 2, www.ny-adelphos.usa
# I can operate on the alias as it were local but it isn't
#
#
# I DO NOT need the password or the actor. The message is
# sent to the other instance.

# the problem is to have a database where the object can be anywhere
# but each federated object can know where to find it.

# I can use the password if I allow a user to login here.
# is this possible? Maybe not.

# the alias belong to a group 0, every group has a single parent


('alias_data', """
create table alias_data(

        local_fk integer references adelphos_ob(adelphos_id),
        actor_fk integer references actor(actor_id) on delete restrict,
        family_fk integer references adelphos_ob(adelphos_id),
        password text

); """),


('view alias_view', """

create view alias_full as select adelphos_id, name, instance_fk,
 created_on, cloned_on, pinned, orphaned, actor_fk, group_zero_fk,
 password from adelphos_ob, alias_data where
 adelphos_id = local_fk;

"""),


('view alias_local', """

create view alias_local as select adelphos_id, name, 
 created_on, cloned_on, pinned, orphaned, actor_fk, group_zero_fk,
 password from adelphos_ob, alias_data where
 (adelphos_id = local_fk) and (alias_data.instance_fk = 0)

"""),



# the trust line can be from two points in adelphos

('trust_line', """

 create table trust_line(

        local_fk integer primary key references adelphos_ob(local_id),

        name text,

        alias_from_fk integer references adelphos_ob(local_id),
        alias_to_fk integer references adelphos_ob(local_id),

        comment text,
        trust_level real

 );

"""),

]


# this is the entrance point to the federated database in adelphos.
class AdelphosDao:

    def _create_schema(self):
        gCon.log("Creating schema...")


        # the schema is an array of statements with a comment
        cursor = self._conn.cursor()

        for cmd in create_schema_sql:
            gCon.log(f"Will exec -> {cmd[0]}")
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


        # I create the specialized DAOs
        self.cur_dao = CurrencyDao(self)
            

    def dump_database(self):
        for line in self._conn.iterdump():
            gCon.log(f"{line}")


    # I can have differenct DAOs which are linked to me.
    def currency_dao(self):
        return self.cur_dao


    def export_to_remote_dto(ctx):
        pass


    # this function will query a remote DAO to get the object (it will
    # be saved locally as a cache)
    async def import_from_dao_remote(ctx, object_uri):

        # I have to split the uri, get the local and the remote part.
        object_splits = object_uri.split('@')

        # Now I have to gquery the remote db.
        local_uri = object_splits[0]
        ctx.rem_instance = object_splits[1]
        
        rcmd = {

                'cmd' : 'daoq',
                'local_uri': local_uri
                }

        ctx.daemon_post_ob = rcmd
        await daemon_remote_query(ctx)


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
        newid = cur.lastrowid
        cur.close()

        ctx.need_commit = True
        return newid
        

    def close(self):
        gCon.log("Shut down the database")
        if (self.mem_db == True):
            self.dump_database()
        self._conn.close()


    def commit(self):
        self._conn.commit()


