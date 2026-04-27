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
# This is the base class of all the world in Adelphos
# this is agnostic relative to the interface above (GUI or CLI)
# and the implementation below (which can be a DB or anything else)

# It contains only the logic of the fractal trust network

# no authorization or authentication is done here, the class
# assumes that these are handled at outer layers.

# usually the functions in this class return 0 on OK, -errno in case
# of error 

# in case a negative value is a valid answer the function will return None
# and the last error is set in the object.

# each action is part of a transaction.

# from argon2 import PasswordHasher
import re

from app.dao.AdelphosUri import uriparse_type, EAdelphosType
from app.core.algo.AdelphosAlgo import AdelphosAlgo 
#from app.core.InstancesModel import InstancesModel

from app.logging import gCon

from app.federation.SocialListener import SocialListener
from app.consts import DAEMON_ID
from app.logging import exit_err
from app.federation.FederatedStore import FederatedStore
from app.ap_api.ActivityPubMockup import ActivityPubMockup
from app.cli.ConnHandler import ConnHandler

import asyncio


# this key is present in the db only if the initialization is done.

ADELPHOS_VERSION_KEY = '__adelphos_v'

# just a small number, it will be incremented at each iteration.
ADELPHOS_CURRENT_VERSION = '0.1'

# Adelphos is the main object which orchestrates all the messages.
class Adelphos(SocialListener):


    def __init__(self, config, instance_name, db, transport):
        self.config = config
        self.instance = instance_name

        # this will be removed. We use here the Federated Store
        self.db = db

        host_name = config['General']['host']
        # I can build a federated store with a local db and a transport
        self.fdb = FederatedStore(host_name, db, transport)
        self.social = ActivityPubMockup(config, True, transport)
        self.cli = ConnHandler(self, transport)

        # this is the controller part. 
        # we pass to the algo the federated store!
        self.aa = AdelphosAlgo(0, self.fdb)

        # I have a set of instances, myself and the allowed ones. 
        #self.instances = InstancesModel()

        # I register myself to the social network
        self.social.register_listener(self)

        # I register the routes: these are my connections to the outside.
        transport.register_routes(self.social)
        transport.register_routes(self.cli)

        cur_version = self.db.get_maybe(ADELPHOS_VERSION_KEY)
        if cur_version is None:
            self.initialization()
            self.db.set(ADELPHOS_VERSION_KEY, ADELPHOS_CURRENT_VERSION)
            self.db.commit()
        else:
            self.load_fixture()


    def load_fixture(self):

        self.social.load_fixture()
        self.get_local_daemon()


    def is_debug(self):
        return self.config['General']['debug']


    def is_test_instance(self):
        test_instance = re.match("_test_", self .instance) is not None
        return test_instance


    def get_local_daemon(self):
        self.ssn = self.social.get_local_user(DAEMON_ID)


    def create_myself_as_actor(self):
        # I publish myself in the social network as a daemon in my server.
        # the return code is more or less like a Social Security Number
        self.ssn = self.social.create_user(DAEMON_ID, True)


    def create_test_users(self):

        if (self.config.get('demo_users') is None):
            gCon.log("no demo users defined")
            return

        demo_users = self.config['demo_users']

        for demo_user in demo_users:
            is_root = demo_user.get('root') == True
            self.create_demo_user(demo_user['name'], demo_user['alias'],
                        demo_user['password'], is_root)


    def _add_root_alias(self, actor_id):
        self.aa.alias_algo.alias_create_hashed(actor_id, 'root', 'admins',
                self.config['General']['root_password'])


    def create_demo_user(self, name, alias_uri, password, is_root):
        #gCon.log(f"Creating ap_actor {name} with alias {alias} and password {password}")
        actor_id = self.social.create_internal_user(name)

        # this is the part which is not relative to activity pub.
        alias_id = self.aa.alias_algo.alias_create_uri(actor_id, alias_uri, password)

        #self.app.kernel.alias_uri_create(actor_id, alias, password)
        if is_root:
            self._add_root_alias(actor_id)


    def create_root_actor(self, root_user):

        actor_id = self.social.discover_user(root_user, True)

        if (actor_id is None):
            exit_err(f"Misconfigured root user {root_user}, cannot resolve.")

        self._add_root_alias(actor_id)



    def initialization(self):

        self.social.initialization()


        # Now I have to discover the root actor.
        #flag = self.dao.created_schema_flag()
        ##del self._init_schema
        #if (flag == False):
        #    return
        self.create_myself_as_actor()

        # Now I want to create some other aliases, this MUST BE DONE before,
        # because the root actor might be internal.
        self.create_test_users()

        # when I return from this function the test users are created, so
        # I can create the root.
        #self.create_root()

        # we have to discover the root actor
        # in another task, because we might be the target!
        root_user = self.config['General']['root_user']
        #gCon.log(f"Creating root user {root_user} for {self.instance}")
        if (root_user != ':local:'):
            self.create_root_actor(root_user)

        #gCon.rule(f"COMMIT OF INITIAL DB (minus the root actor) for {self.instance}")
        self.db.commit()


    async def new_post(self, post):
        pass


    # the aliases subsystem
    #def alias_ss(self):
    #    return self.alias_ss


    #def add_federated_adelphos(self, other_adelphos):
    #    pass




