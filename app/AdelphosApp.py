# the main class of adelphos. This defines the application.


from fastapi import FastAPI
import os

from app.consts import ADELPHOS_AP_ENV_KEY
from app.logging import exit_err
from app.logging import gCon

app = None

# I create here the main application object, singleton
def get_app():
    global app
    while True:
        if (app is not None):
            return app

        instance_name = os.getenv(ADELPHOS_AP_ENV_KEY)

        if (instance_name is None):
            exit_err(f"{ADELPHOS_AP_ENV_KEY} variable not defined")

        gCon.log(f"start instance {instance_name}")
        app = AdelphosApp(instance_name, root_path="/api")


class AdelphosApp(FastAPI):

    # the app has inside the context shared by all the modules.

    def __init__(self, instance: str, **kwargs):
        super().__init__(**kwargs)
        self.instance = instance
