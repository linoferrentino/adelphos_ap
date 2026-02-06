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
from app.consts import USER_ID
from app.consts import API_POINT

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

#('enable foreign keys',
# """
# PRAGMA foreign_keys = ON;
# """),


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
    actor_fk integer primary key,
    authorized text,
    comment text,
    timestamp text default current_timestamp,
    foreign key (actor_fk) references ap_actor(actor_id)
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

create table fd_actor(
    fd_actor_id integer primary key,
    name text,
    instance_fk integer not null references ad_instance(actor_fk),
    timestamp text default current_timestamp
    );
 """),


# this is the base class for all the 'inert' objects in adelphos.  they are
# created by a federated actor (an alias), and they follow him if he moves.
('fd_object', """
create table fd_object(
    fd_object_id integer primary key,
    name text,
    creator_fk integer references fd_alias(local_fk) on delete restrict,
    timestamp text default current_timestamp
 );"""),


# I must create an index on name, as I will sometimes query on this.


# the currency is the base of exchange. In adelphos we do not have a
# centralized value exchange, the exchange rates are decided by the actor
# themselves.
('currency', """
create table fd_currency(

        local_fk integer primary key references fd_object(local_id),
        symbol text,
        human_value real

);"""),


#('fd base_fractal_group', """
#
#create table fd_base_fractal_group(
#
#        local_fk integer primary key references fd_actor(fd_actor_id),
#        parent_group_fk integer references fd_group(local_fk),
#        equity real,
#
#);
#
# """),


# the federated group can have a parent and many children
# it has a boss and a cashier
# the parent group need not to belong to the same instance
# (the same for its members!).
# this table is for families (level 0) and groups (level > 0)
# this is a concrete table where the discriminator column is level.
('fd group', """
create table fd_group_family(

        local_fk integer primary key references 
             fd_actor(fd_actor_id),
        boss_or_founder_fk integer references fd_alias(local_fk),
        cashier_fk integer references fd_alias(local_fk),
        currency_fk integer references fd_currency(local_fk),
        level integer,
        equity real

);"""),


# the alias is the link between adelphos and activity pub; this means
# that we have both the links.
# an actor can have different aliases in different families.
# an actor cannot have two aliases in the same family
# lino.ferrentino, lino_ferre@mastodon.uno OK
# lino1.ferrentino, lino_ferre@mastodon.uno NO
('fd_alias', """
create table fd_alias(

        local_fk integer references fd_actor(fd_actor_id),
        actor_fk integer references ap_actor(actor_id) on delete restrict,
        family_fk integer references fd_group_family(local_fk),
        password text,
        primary key (local_fk, actor_fk, family_fk)

) without rowid; """),



# the family is the basic group in adelphos
# the level is zero implicit.


#('family', """
#create table fd_family (
#
#        local_fk integer primary key references fd_actor(fd_actor_id),
#        family_chief_fk integer references fd_alias(local_fk),
#        parent_group_fk text references fd_group(local_fk),
#        currency_fk integer references fd_currency(local_fk),
#        equity real
#
#);"""),
#
#
## this view joins the family with the actor and the adelphos object 
#('view family_actor_raw', """
#
#
# create view family_raw as select fd_object_id, name, creator_fk,
#    timestamp, act.name, act.instance_fk, act.timestamp,
#    parent_group_fk, currency_fk, equity from
#    fd_object, fd_family, fd_actor as act where
#    ( (local_fk = fd_object_id)
#    and
#    (creator_fk = fd_actor_id)
#    );
#
# """),
#
#
## this view selects all the local families.
## the instance zero is by definition the local adelphos instance.
#('view family_local_raw', """
#
#
# create view family_local_raw as select fd_object_id, name, creator_fk,
#    timestamp, parent_group_fk, currency_fk, equity from
#    fd_object, fd_family, fd_actor  where
#    ( (local_fk = fd_object_id)
#    and
#    (creator_fk = fd_actor_id)
#    and
#    (instance_fk = 0)
#    );
#
# """),


# here we have the federated family and the federated alias, they are all
# "actors", in the sense that they are 'alive'


# there are three types of alive objects in adelphos: the group, the
# family and the alias: they form the trust web.

# the family is the base class for all the 




]


# this is the entrance point to the federated database in adelphos.
class AdelphosDb:


    def _create_schema(self, app):
        gCon.log("Creating schema...")

        # I can add the foreign key constraints only without a transaction.
        self._conn.execute("pragma foreign_keys = ON;")

        gCon.log("I restore the autocommit")
        self._conn.autocommit = False

        cursor = self._conn.cursor()

        for cmd in create_schema_sql:
            gCon.log(f"Will exec -> {cmd[0]}")
            cursor.execute(cmd[1])

        # Now I store the initial data (for example the zero actor,
        # which is myself)
        host = app.config['General']['host']

        # I insert myself as the instance zero
        # here interpolating the SQL is safe, the values do not come
        # from the outside.
        sql_insert = f"""
insert into ap_server(server_id, host_name) values (0, '{host}');"""
        cursor.execute(sql_insert)

        user_path = API_POINT + f"/users/{USER_ID}"
        user_inbox = user_path + "/inbox"

        sql_insert = f"""
insert into ap_actor (actor_id, server_fk, user_path, inbox_path,
preferred_username, public_key) values(0, 0, "{user_path}",
"{user_inbox}", "{USER_ID}", "{app.public_key}")

        """
        cursor.execute(sql_insert)

        sql_insert = f"""

insert into ad_instance(actor_fk, authorized, comment) values
(0, 1, "Local adelphos instance")
        """
        cursor.execute(sql_insert)

        cursor.close()

        self._conn.commit()


    # for testing I can also create the file in memory
    def __init__(self, app):

        config = app.config

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

        # create the connection, autocommit will be False after we
        # set the primary keys
        self._conn = sqlite3.connect(db_name_complete,
                                     autocommit=True)

      
        if (create_schema == True):
            self._create_schema(app)

           

    def dump_database(self):
        for line in self._conn.iterdump():
            gCon.log(f"{line}")


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


    def rollback(self):
        self._conn.rollback()
