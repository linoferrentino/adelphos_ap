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

app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.dao = AdelphosDao(app.config)
    yield
    app.dao.close()


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
        self.instance = instance

        # load the configuration.
        self.config = load_conf(instance)

        # load the keys
        (pub_key, priv_key) = load_keys(self.config)
        self.public_key = pub_key
        self.private_key = priv_key
        


