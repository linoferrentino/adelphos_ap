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
from app.dao.ActorDto import ActorDao
from app.dao.ServerDto import ServerDao
from app.consts import USER_ID

# I import here the specialized DAOs to access the federated objects.



create_schema_sql = \
[
        

# we store here the information about the activity pub servers
# around us.
# For the purpose of adelphos a server is just a container of actors.
# adelphos itself is an activity pub server, but a special one, because
# it has only one published actor, the adelphos daemon.

# the server zero is the local server, it corresponds to the local adelphos
# instance.

# an adelphos server is also an activity pub server, but the contrary
# is not true.
# all the adelphos servers join the federated adelphos database.
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


# this is the view that joins the two tables.
('view actor_server',
 """
 create view actor_server as select
 actor_id, host_name, user_path, inbox_path, preferred_name,
 public_key, ap_actor.timestamp as timestamp from ap_server, ap_actor where
 server_id = server_fk;

"""),


# this is the table that stores the adelphos instances. These
# are not activity pub instances.
# However every adelphos instance is linked to an activity pub actor
# which is its endpoint for the fediverse.
('instance', """
create table ad_instance (
    actor_fk integer primary key references ap_actor(actor_id),
    authorized text,
    comment text,
    timestamp text default current_timestamp

);"""),


# The basis of the adelphos federated database is the adelphos object:
# the adelphos object is linked to an adelphos instance and to an alias
# in the same instance.
# an alias belong to an instance and all the object he creates belong
# there.

# users, groups and families are alive
# objects are... objects.


# this is the base class for all the 'alive' objects in adelphos,
# they can be participant in transactions and be creators and stores
# of objects.
# they can be linked, and they belong to an instance.
# all the objects an actor creates are stored in that instance.
# if the actor moves the objects he has created move with him.
('fd_actor', """
    fd_actor_id integer primary key,
    name text,
    instance_fk integer not null integer references ad_instance(actor_fk),
    timestamp text default current_timestamp
 """),


# this is the base class for all the 'inert' objects in adelphos.
# they are created by an actor, and they follow him if he moves.
('fd_object', """
    fd_object_id integer primary key,
    name text,
    creator_fk integer references fd_actor(fd_actor_id) on delete restrict,
    timestamp text default current_timestamp
 """),


# the currency is the base of exchange. In adelphos we do not have a
# centralized value exchange, the exchange rates are decided by the actor
# themselves.
('currency', """
create table fd_currency(

        local_fk integer primary key references fd_object(local_id),
        symbol text,
        human_value real

);"""),


# the federated group can have a parent and many children
# it has a boss and a cashier
# the parent group need not to belong to the same instance
# (the same for its members!).
('group', """
create table fd_group(

        local_fk integer primary key references adelphos_ob(local_id),
        boss_fk integer references fd_actor(fd_actor_id),
        cashier_fk integer references fd_actor(fd_actor_id),
        parent_group_fk integer references fd_group(local_fk),
        equity real,
        level integer

);"""),



# here we have the federated family and the federated alias, they are all
# "actors", in the sense that they are 'alive'


# there are three types of alive objects in adelphos: the group, the
# family and the alias: they form the trust web.




# the family is the base class for all the 


# the alias is the link between adelphos and activity pub; this means
# that we have both the links.
('fd_alias', """
create table fd_alias(

        local_fk integer references fd_actor(fd_actor_id),
        actor_fk integer references ap_actor(actor_id) on delete restrict,
        family_fk integer references adelphos_ob(adelphos_id),
        password text

); """),




# every object in adelphos (apart from the aliases) has a creator who
# is an alias. The alias has a creator who is an actor.
# The alias is the bridge between the world of adelphos and the
# the world of Activity Pub
# every adelphos object has a home instance, from it we define its URI

# The fact is that every ALIAS has an instance: the objects are tied
# to the alias, probably not every object needs to have a instance,
# but only the alias.

#('adelphos_ob', """
#create table adelphos_ob(
#
#        adelphos_id integer primary key,
#        creator_fk integer references alias(adelphos_id),
#        name text,
#        instance_fk not null integer references ad_instance(actor_fk),
#        created_on text default current_timestamp
#
#
#);""") ,

# a group has only one parent, like a file system. We do not support
# a mesh like ripple, even if a ripple can be created by following
# the trust lines.

# a person can be thought as a level zero, even if we do have
# different levels.





# the family is the basic group in adelphos
# the level is zero implicit.


('family_data', """
create table family_data(

        local_fk integer primary key references adelphos_ob(local_id),

        parent_group_fk text references ad_group(local_fk),

        currency_fk integer references currency_data(local_fk),

        equity real


);"""),


#('view family_raw', """
#create view family_raw as select adelphos_id, name, instance_fk, created_on,
# pinned, orphaned, parent_group_fk, currency_fk, equity from
# family_data, adelphos_ob where
# ( (family_data.local_fk = adelphos_ob.adelphos_id) and
#   (adelphos_ob.instance_fk = 0) );
#"""),




#('view family_local', """
#create view family_local as select adelphos_id, name, created_on,
# pinned, orphaned, parent_group_fk, currency_fk, equity from
# family_data, adelphos_ob where
# ( (family_data.local_fk = adelphos_ob.adelphos_id) and
#   (adelphos_ob.instance_fk = 0) );
#
#"""),
#
#
#
#
#('view alias_view', """
#
#create view alias_full as select adelphos_id, name, instance_fk,
# created_on, cloned_on, pinned, orphaned, actor_fk, group_zero_fk,
# password from adelphos_ob, alias_data where
# adelphos_id = local_fk;
#
#"""),
#
#
#('view alias_local', """
#
#create view alias_local as select adelphos_id, name, 
# created_on, cloned_on, pinned, orphaned, actor_fk, group_zero_fk,
# password from adelphos_ob, alias_data where
# (adelphos_id = local_fk) and (alias_data.instance_fk = 0)
#
#"""),
#
#
#
## the trust line can be from two points in adelphos
#
#('trust_line', """
#
# create table trust_line(
#
#        local_fk integer primary key references adelphos_ob(local_id),
#
#        name text,
#
#        alias_from_fk integer references adelphos_ob(local_id),
#        alias_to_fk integer references adelphos_ob(local_id),
#
#        comment text,
#        trust_level real
#
# );
#
#"""),

]


# this is the entrance point to the federated database in adelphos.
class AdelphosDao:

    def _create_schema(self, config):
        gCon.log("Creating schema...")


        # the schema is an array of statements with a comment
        cursor = self._conn.cursor()

        for cmd in create_schema_sql:
            gCon.log(f"Will exec -> {cmd[0]}")
            cursor.execute(cmd[1])

        # Now I store the initial data (for example the zero actor,
        # which is myself)
        #host = app.config['General']['host']
        

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
            self._create_schema(config)


        # I create the specialized DAOs
        self.currency_dao = CurrencyDao(self)
        self.actor_dao = ActorDao(self)
        self.server_dao = ServerDao(self)
            

    def dump_database(self):
        for line in self._conn.iterdump():
            gCon.log(f"{line}")


    # I can have differenct DAOs which are linked to me.
    #def currency_dao(self):
    #    return self.cur_dao


    #def actor_dao(self):
    #    return self.actor_dao


    def export_to_remote_dto(ctx):
        pass


    # this function will query a remote DAO to get the object (it will
    # be saved locally as a cache)
    async def import_from_dao_remote(ctx, object_uri):

        # I have to split the uri, get the local and the remote part.
        #object_splits = object_uri.split('@')

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


    # A generic function to insert a data object.
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


