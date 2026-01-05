# the main class of adelphos. This defines the application.


from fastapi import FastAPI
import os

from app.consts import ADELPHOS_AP_ENV_KEY
from app.consts import API_POINT

from app.logging import exit_err
from app.logging import gCon

from app.config import load_conf
from app.keys import load_keys

from app.dao.AdelphosDao import AdelphosDao
from contextlib import asynccontextmanager
import aiohttp
import asyncio

app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.dao = AdelphosDao(app.config)
    asyncio.create_task(session_worker(app))
    yield
    # no more running, please.
    app.running = False
    app.dao.close()

    # signal all the tasks to stop 
    async with app.cond:
        app.cond.notify_all()


async def client_request_async(session, req):
    gCon.log(f"will request the url {req._url}")
    async with session.get(req._url) as resp:
        req.status_code = resp.status
        req.text = await resp.text()

    gCon.log(f"got response {req.status_code} now I signal")

    # Ok, now I can signal the waiting task
    async with req._cond:
        req._cond.notify()


async def client_post_async(session, req):
    gCon.log(f"will post to url {req._url}")
    async with session.post(req._url, headers = req._headers):
        pass
     

# this is the session worker that holds the session and
# does the async requests.
async def session_worker(app: FastAPI):

    headers_acc = {"Accept" : "application/activity+json"}
    async with aiohttp.ClientSession(headers = headers_acc) as session:
        # this is the never ending cycle
        while app.running == True:
            async with app.cond:
                while (len(app.requests) != 0):
                    # fifo order
                    req = app.requests.pop(0)
                    if (req._method == "get"):
                        asyncio.create_task(client_request_async
                                            (session, req))
                    elif (req._method == "post"):
                        asyncio.create_task(client_post_async
                                            (session, req))

                # No more
                gCon.log("No request to do, I wait")
                await app.cond.wait()
                gCon.log("woken up!")


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

        # create the condition for the http requests.
        self.cond = asyncio.Condition()  

        # this is the list of requests.
        self.requests = list()

        # and start the task
        #self.client_task = asyncio.run(session_worker(self))


    async def async_req_push(self, ar):
        async with self.cond:
            self.requests.append(ar)
            self.cond.notify()


    async def async_req_wait(self, ar):
        # I have to put it into the list and wait
        await self.async_req_push(ar)
        gCon.log(f"async req to {ar._url} posted, now I wait")
        while (ar.status_code is None):
            async with ar._cond:
                await ar._cond.wait()

        gCon.log(f"got result {ar.status_code} in client request!")


