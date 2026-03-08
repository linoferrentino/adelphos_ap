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
# the main class of adelphos. This defines the application.

from fastapi import FastAPI
import os

from app.consts import ADELPHOS_AP_ENV_KEY
from app.consts import API_POINT
from app.consts import USER_ID

from app.logging import exit_err
from app.logging import gCon

from app.cli.ConnHandler import ConnHandler

from app.config import load_conf
from app.keys import load_keys

from app.dao.AdelphosDb import AdelphosDb
from contextlib import asynccontextmanager
import aiohttp
import asyncio

from app.ap_api.ActivityPubApi import ActivityPubApi

# the actor is ambiguous, we can have the activity pub actor
# or the adelphos actor
from app.dao.ApActorDao import ApActorDao
from app.dao.ApActorDto import create_ap_actor

from app.dao.ApServerDao import ApServerDao
from app.dao.ApServerDto import create_ap_server

from app.dao.FamilyDao import FamilyDao
from app.dao.CurrencyDao import CurrencyDao 
from app.dao.AliasDao import AliasDao
from app.dao.AdInstanceDao import AdInstanceDao
from app.dao.AdInstanceDto import create_ad_instance

from app.api.ActivityPubGateway import ActivityPubGateway
from .consts import GENERAL_SECTION, PRIVATE_KEY_FILE_KEY

app = None


class AdelphosApp(FastAPI):


    # the initialization of adelphos is done in two steps.
    def __init__(self, **kwargs):

        super().__init__(**kwargs)


    # we can init the instance using also a memory configuration,
    # to use in testing.
    # the configuration can be any json which is interpreted.
    def init_instance(self, instance, config = None):

        self.running = True
        self.instance = instance

        # load the configuration.
        if (config is None):
            self.config = load_conf(instance)
        else:
            self.config = config

        # load the keys
        key_file = self.config[GENERAL_SECTION][PRIVATE_KEY_FILE_KEY]
        (pub_key, priv_key) = load_keys(key_file)
        self.public_key = pub_key
        self.private_key = priv_key

        self.ap_gateway = ActivityPubGateway(self)

        # create the condition for the http requests and the daemon
        # background cycle.
        self.cond = asyncio.Condition()  

        # this is the queue of requests that this daemon does
        # to the outside.
        self.requests = list()
        self._init_schema = False


    def post_initialization_needed(self):
        self._init_schema = True


    async def post_initialization(self):
        # Now I have to discover the root actor.
        flag = self._init_schema
        del self._init_schema
        if (flag == False):
            return

        self.create_myself_as_actor()

        await self.create_root_actor()

        self.create_test_users()

        # Now I want to create some other aliases.
        gCon.rule("========= FINAL COMMIT OF INITIAL DB =======")
        self.dao.commit()


    # this will create the zero server, the zero actor and the zero instance.
    def create_myself_as_actor(self):
        
        # create myself as a server, with a fixed id of zero
        host = self.config['General']['host']
        myself_server = create_ap_server(host)
        myself_server.server_id = 0
        my_server_id = self.dao.ap_server_dao.store_full_no_ts(myself_server)
        gCon.log("Created the server")

        self.create_app_actor(USER_ID, 0)

        # now create the instance.
        myself_instance = create_ad_instance(0, 1, "Local adelphos instance")
        my_instance_id = self.dao.ad_instance_dao.store_full_no_ts(myself_instance)
        gCon.log("Created the instance")


    # creates an actor which sits in the instance (only useful for testing)
    def create_app_actor(self, actor_name, forced_id = None):
        user_path = API_POINT + f"/users/{actor_name}"
        user_inbox = user_path + "/inbox"
        # the server is hard coded to zero, we are in the app realm
        myself_actor = create_ap_actor(0, user_path, user_inbox,
                                       actor_name, self.public_key)
        if (forced_id is not None):
            myself_actor.actor_id = 0
            actor_id = self.dao.ap_actor_dao.store_full_no_ts(myself_actor)
        else:
            actor_id = self.dao.ap_actor_dao.store(myself_actor)

        gCon.log(f"Created actor {actor_name} with id {actor_id}")
        return actor_id


    def create_test_users(self):

        if (self.config.get('demo_users') is None):
            gCon.log("no demo users defined")
            return

        demo_users = self.config['demo_users']
        for demo_user in demo_users:
            # by definition the users belong tj my server.
            # they are ``embedded'' in this instance, so they belong to
            # ap_server 'zero'
            gCon.log(f"I want to create {demo_user}")
            # first of all I have to create the actor, the server is our server
            # and his/her key is the application's key.
            actor_id = self.create_app_actor(demo_user['name'])
            # Now I will create the alias.
            gCon.log(f"The new actor has the id {actor_id}")
            # I have to create the alias, using the alias and the password
            self.ap_gateway.ap_alias_api.create_alias_pass(
                    actor_id, demo_user['alias'], demo_user['password'])


    async def create_root_actor(self):
        
        root_user = self.config['General']['root_user']
        gCon.log(f"Will discover root {root_user}")
        # here I will get the activity pub object and I will create the root alias
        (root_server, root_actor) = await self.ap_api.get_or_discover_actor(root_user)

        # Now I have to create the alias, so I use tha ApAliasApi.
        self.ap_gateway.ap_alias_api.create_alias_impl(root_actor.actor_id,
                                               'admins', 'root',
                                               self.config['General']['root_password'])


    # this is used for the put request.
    # XXX maybe we have to schedule a repeat interval.
    async def async_req_push(self, ar):
        async with self.cond:
            self.requests.append(ar)
            self.cond.notify_all()


    # returns the internet name of this adelphos instance: this is used
    # to differentiate local from federated objects.
    def get_local_host(self):
        # Just to not disperse too many hardcoded strings around.
        return self.config['General']['host']


    def is_debug(self):
        return self.config['General']['debug']


    # this is the blocking (async) GET request.
    async def async_req_wait(self, ar):
        # I have to put it into the list and wait
        await self.async_req_push(ar)
        gCon.log(f"async req to {ar._url} posted, now I wait")
        while (ar.status_code is None):
            async with ar._cond:
                await ar._cond.wait()

        gCon.log(f"got result {ar.status_code} in client request!")


# A simple container for all the DAOs in the system
class MasterAdelphosDao:


    def __init__(self, app):
        gCon.log("Creating the Master DAO, first the connection")
        self.db = AdelphosDb(app)
        # I take a reference to the application for the configuration
        self.app = app

        gCon.log("Creating here the specialized DAOs")

        # I create the specialized DAOs
        self.currency_dao = CurrencyDao(self)
        self.ap_actor_dao  = ApActorDao(self)
        self.ap_server_dao   = ApServerDao(self)
        self.ad_instance_dao = AdInstanceDao(self)
        self.family_dao  = FamilyDao(self)
        self.alias_dao   = AliasDao(self)


    def close(self):
        self.db.close()


    def commit(self):
        self.db.commit()


    def rollback(self):
        self.db.rollback()



@asynccontextmanager
async def lifespan(app: AdelphosApp):
    app.dao = MasterAdelphosDao(app)
    ses_worker = asyncio.create_task(session_worker(app))
    daemon_worker = asyncio.create_task(daemon_bg_cycle(app))
    app.conn_hndl = ConnHandler(app)
    app.ap_api = ActivityPubApi(app)

    # post init
    gCon.log("Application post initialization start.")
    await app.post_initialization()
    gCon.log("App is ready.")
    yield

    # no more running, please.
    app.running = False
    # signal the workers to stop 
    async with app.cond:
        app.cond.notify_all()
    gCon.log("Please wait for adelphos shutdown")
    app.ap_api.close()
    await app.conn_hndl.stop()
    await ses_worker
    await daemon_worker
    # the last to close is the DB, so that all the modules have a chance to save
    # on DB their transient state.
    app.dao.close()


# this method is called with the app.cond taken.
# this method will take all the requests in queue and start
# their soft-thread
async def _dequeue_requests_or_wait_lock(session, app: AdelphosApp):
     
    while (len(app.requests) != 0):
        req = app.requests.pop()
        asyncio.create_task(req.async_req(session))

    gCon.log("No requests, I wait")
    await app.cond.wait()
    gCon.log("woken up!")


async def daemon_bg_cycle(app: AdelphosApp):

    while app.running == True:
        async with app.cond:
            try:
                res = await asyncio.wait_for(app.cond.wait(),
                                             timeout = 3.0)
                # If I have a 'normal' notification I do not do anything,
                # this is a message for the session_worker
            except asyncio.TimeoutError:
                    #gCon.log("Now I can do a cycle")
                    pass

    gCon.log("Daemon quit.")


# this is the session worker that holds the session and
# does the async requests 
async def session_worker(app: AdelphosApp):

    headers_acc = {"Accept" : "application/activity+json"}

    async with aiohttp.ClientSession(headers = headers_acc) as session:
        # this is the never ending cycle
        while app.running == True:
            async with app.cond:
                await _dequeue_requests_or_wait_lock(session, app)

        gCon.log("Session worker quit.")
                

# I create here the main application object, singleton
def get_app(instance_name = None, config = None):
    global app

    if (app is not None):
        return app

    if (instance_name is None):
        instance_name = os.getenv(ADELPHOS_AP_ENV_KEY)

    if (instance_name is None):
        exit_err(f"No instance defined and {ADELPHOS_AP_ENV_KEY} variable not defined")

    gCon.log(f"Starting Adelphos' instance {instance_name}")
    app = AdelphosApp(root_path = API_POINT, lifespan = lifespan)

    app.init_instance(instance_name, config)

    return get_app()



