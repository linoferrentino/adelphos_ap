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

import os
import aiohttp
import asyncio
import re


from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.consts import ADELPHOS_AP_ENV_KEY
from app.consts import API_POINT
from app.consts import USER_ID

from app.dao.AdelphosUri import EAdelphosType
from app.dao.AdelphosUri import uriparse

from app.dao.AdelphosDb import AdelphosDb
from app.logging import exit_err
from app.logging import gCon

from app.cli.ConnHandler import ConnHandler

from app.config import load_conf
from app.keys import load_keys
from app.logging import good_bye

from app.ap_api.ActivityPubApi import ActivityPubApi
from app.ap_api.ActivityPubMockup import ActivityPubMockup

# the actor is ambiguous, we can have the activity pub actor
# or the adelphos actor

from app.dao.ApServerDao import ApServerDao
from app.dao.ApServerDto import create_ap_server

from app.core.MasterAdelphosDao import MasterAdelphosDao

from app.dao.AdInstanceDto import create_ad_instance

from app.ap_api.ActivityPubGateway import ActivityPubGateway
from app.ad_api.AdelphosGateway import AdelphosGateway
from .consts import GENERAL_SECTION, PRIVATE_KEY_FILE_KEY
from app.AdelphosRouter import make_router
from app.core.Adelphos import Adelphos

from app.store.MemoryStore import MemoryStore

app = None


class AdelphosApp(FastAPI):


    # the initialization of adelphos is done in two steps.
    def __init__(self, instance, **kwargs):

        super().__init__(**kwargs)
        self.instance = instance


    # we can init the instance using also a memory configuration,
    # to use in testing.
    # the configuration can be any json which is interpreted.
    # or a configuration file
    def init_instance(self, config_file, config):

        self.running = True

        # load the configuration.
        if (config is None):
            self.config = load_conf(self.instance, config_file)
        else:
            self.config = config

        # load the keys
        #key_file = self.config[GENERAL_SECTION][PRIVATE_KEY_FILE_KEY]
        ##gCon.log(f"Get private key from {key_file}")
        #(pub_key, priv_key) = load_keys(key_file)
        #self.public_key = pub_key
        #self.private_key = priv_key

        # I have two gateways, one which uses activity pub, the other
        # is the enclosed gateway tunneled inside activity pub.
        #self.ap_gateway = ActivityPubGateway(self)
        self.ad_gateway = AdelphosGateway(self)
        #self.ap_mockup = ActivityPubMockup(self)

        # create the condition for the http requests and the daemon
        # background cycle.
        self.cond = asyncio.Condition()  

        # this is the queue of requests that this daemon does
        # to the outside.
        self.requests = list()
        self._init_schema = False


    def post_initialization_needed(self):
        self._init_schema = True


    # the app can have some fake Activity Pub users defined for testing,
    # the daemon is always defined.
    def ap_user_exists(self, activity_pub_user):

        if (activity_pub_user == USER_ID):
            return True 
        return self.ap_mockup.ap_user_exists(activity_pub_user)


    def get_ap_mockup(self):
        return self.ap_mockup 


    def ap_user_info(self, activity_pub_user):

        if (activity_pub_user == USER_ID):
            return ('bot', USER_ID, f"Adelphos' daemon for instance {self.instance}")
        return self.ap_mockup.ap_user_info(activity_pub_user)


    async def post_initialization(self):
        # Now I have to discover the root actor.
        #flag = self.dao.created_schema_flag()
        ##del self._init_schema
        #if (flag == False):
        #    return

        self.create_myself_as_actor()

        # Now I want to create some other aliases, this MUST BE DONE before,
        # because the root actor might be internal.
        self.ap_mockup.create_test_users()

        # when I return from this function the test users are created, so
        # I can create the root.

        # we have to discover the root actor
        # in another task, because we might be the target!
        root_user = self.config['General']['root_user']
        #gCon.log(f"Creating root user {root_user} for {self.instance}")
        if (root_user != ':local:'):
            asyncio.create_task(self.create_root_actor(root_user))

        #gCon.rule(f"COMMIT OF INITIAL DB (minus the root actor) for {self.instance}")
        self.dao.commit()


    # this will create the zero server, the zero actor and the zero instance.
    def create_myself_as_actor(self):
        
        # create myself as a server, with a fixed id of zero
        host = self.config['General']['host']
        myself_server = create_ap_server(host)
        myself_server.server_id = 0
        my_server_id = self.dao.ap_server_dao.store_full_no_ts(myself_server)
        #gCon.log("Created the server")

        self.ap_mockup.create_app_actor(USER_ID, 0)

        # now create the instance.
        myself_instance = create_ad_instance(0, 1, "Local adelphos instance")
        my_instance_id = self.dao.ad_instance_dao.store_full_no_ts(myself_instance)
        #gCon.log("Created the instance")


    async def create_root_actor(self, root_user):
        
        # here I will get the activity pub object and I will create the root alias
        (root_server, root_actor) = await self.ap_api.get_or_discover_actor(root_user, True)

        if (root_server is None):
            exit_err(f"Misconfigured root user {root_user}, cannot resolve.")

        self.create_root_actor_impl(root_actor.actor_id)


    def create_root_actor_impl(self, actor_id):

        # Now I have to create the alias
        self.kernel.add_alias(actor_id,
                         'admins', 0, 'root',
                         self.config['General']['root_password'])
        self.kernel.dao.commit()
        #gCon.log(f"[red]DB for  {self.instance} START[/red]")
        #self.dao.db.dump_database()
        #gCon.log(f"[red]DB for  {self.instance} END[/red]")


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


    def is_test_instance(self):
        test_instance = re.match("_test_", self .instance) is not None
        return test_instance


    # this is the blocking (async) GET request.
    async def async_req_wait(self, ar):
        # I have to put it into the list and wait
        await self.async_req_push(ar)
        #gCon.log(f"async req to {ar._url} posted, now I wait")
        while (ar.status_code is None):
            async with ar._cond:
                await ar._cond.wait()

        #gCon.log(f"got result {ar.status_code} in client request!")
        return ar.status_code




@asynccontextmanager
async def lifespan(app: AdelphosApp):
    #gCon.rule(f"LIFESPAN START {app.instance}")

    #db_name = app.config['General']['db_name']
    #db = AdelphosDb(db_name)
    db = MemoryStore()
    ap_mockup = ActivityPubMockup(app.config, db, True)
    app.kernel = Adelphos(app.config, app.instance, db, ap_mockup)
    ses_worker = asyncio.create_task(session_worker(app))
    daemon_worker = asyncio.create_task(daemon_bg_cycle(app))
    app.include_router(ap_mockup.get_router())

    #app.ap_api = ActivityPubApi(app)

    # post init
    #gCon.log("Application post initialization start.")
    #await app.post_initialization()
    #gCon.rule(f"App {app.instance} is ready.")
    yield

    # no more running, please.
    app.running = False
    # signal the workers to stop 
    async with app.cond:
        app.cond.notify_all()
    #gCon.log("Please wait for adelphos shutdown")
    #app.ap_api.close()
    await app.conn_hndl.stop()
    await ses_worker
    await daemon_worker
    # the last to close is the DB, so that all the modules have a chance to save
    # on DB their transient state.
    #app.dao.close()
    db.close()


# this method is called with the app.cond taken.
# this method will take all the requests in queue and start
# their soft-thread
async def _dequeue_requests_or_wait_lock(session, app: AdelphosApp):
     
    while (len(app.requests) != 0):
        req = app.requests.pop()
        asyncio.create_task(req.async_req(session))
    await app.cond.wait()


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

    #gCon.log("Daemon quit.")


# this is the session worker that holds the session and
# does the async requests 
async def session_worker(app: AdelphosApp):

    headers_acc = {"Accept" : "application/activity+json"}

    async with aiohttp.ClientSession(headers = headers_acc) as session:
        # this is the never ending cycle
        while app.running == True:
            async with app.cond:
                await _dequeue_requests_or_wait_lock(session, app)

        #gCon.log("Session worker quit.")
                

# I create here the main application object, singleton
def get_app(instance_name, config_file, config):
    global app

    if (app is not None):
        return app

    if (instance_name is None):
        instance_name = os.getenv(ADELPHOS_AP_ENV_KEY)

    if (instance_name is None):
        exit_err(f"No instance defined and {ADELPHOS_AP_ENV_KEY} variable not defined")

    #gCon.log(f"Starting Adelphos' instance {instance_name}")
    app = AdelphosApp(instance_name, root_path = API_POINT, lifespan = lifespan)

    #router = make_router(app)

    app.conn_hndl = ConnHandler(app)
    app.include_router(app.conn_hndl.get_router())

    app.init_instance(config_file, config)

    return app


# this does not try to create it.
def get_existent_app():
    return app


def del_app():
    global app
    if (app is None):
        return
    del app
    app = None
