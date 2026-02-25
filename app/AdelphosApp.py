# the main class of adelphos. This defines the application.


from fastapi import FastAPI
import os

from app.consts import ADELPHOS_AP_ENV_KEY
from app.consts import API_POINT

from app.logging import exit_err
from app.logging import gCon

from app.cli.ConnHandler import ConnHandler

from app.config import load_conf
from app.keys import load_keys

from app.dao.AdelphosDb import AdelphosDb
from contextlib import asynccontextmanager
import aiohttp
import asyncio

# the actor is ambiguous, we can have the activity pub actor
# or the adelphos actor
from app.dao.ApActorDao import ApActorDao
# also the server is ambiguous: we can have the ActivityPub server
# and the adelphos server, which is an instance

from app.dao.ApServerDao import ApServerDao
from app.dao.FamilyDao import FamilyDao
from app.dao.CurrencyDao import CurrencyDao 
from app.dao.AliasDao import AliasDao
from app.dao.AdInstanceDao import AdInstanceDao

app = None


class AdelphosApp(FastAPI):


    def __init__(self, instance: str, **kwargs):

        super().__init__(**kwargs)
        self.running = True
        self.instance = instance

        # load the configuration.
        self.config = load_conf(instance)

        # load the keys
        (pub_key, priv_key) = load_keys(self.config)
        self.public_key = pub_key
        self.private_key = priv_key

        # create the condition for the http requests and the daemon
        # background cycle.
        self.cond = asyncio.Condition()  

        # this is the queue of requests that this daemon does
        # to the outside.
        self.requests = list()


    def create_root_user(self):
        # Now I have to discover the root actor.
        pass


    # this is used for the put request.
    # XXX maybe we have to schedule a repeat interval.
    async def async_req_push(self, ar):
        async with self.cond:
            self.requests.append(ar)
            self.cond.notify_all()


    # returns the internet name of this adelphos instance: this is used
    # to differentiate local from federated objects.
    def get_local_host():
        # Just to not disperse too many hardcoded strings around.
        return self.config['General']['host']


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

    yield

    # no more running, please.
    app.running = False
    # signal the workers to stop 
    async with app.cond:
        app.cond.notify_all()
    gCon.log("Please wait for adelphos shutdown")
    await app.conn_hndl.stop()
    await ses_worker
    await daemon_worker
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
def get_app():
    global app

    if (app is not None):
        return app

    instance_name = os.getenv(ADELPHOS_AP_ENV_KEY)

    if (instance_name is None):
        exit_err(f"{ADELPHOS_AP_ENV_KEY} variable not defined")

    gCon.log(f"Starting Adelphos' instance {instance_name}")
    app = AdelphosApp(instance_name, root_path = API_POINT,
                      lifespan = lifespan)

    return get_app()



