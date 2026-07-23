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


import pytest
from contextlib import asynccontextmanager
import multiprocessing as mp
import contextlib
import uvicorn
from app.transport.async_mode.StarletteHelper import starlette_app_creator
import time
#from app.consts import API_POINT, LOCALHOST
from app.consts import LOCALHOST
from app.sdc.Dependencies import Dependencies
from app.logging import gCon


class ProcessWrapper:

    @contextlib.contextmanager
    def run_in_subprocess(self, builder, parms, port):
        p = mp.Process(target = start_starlette_app, args = (builder, parms, port))
        p.start()
        try:
            yield
        finally:
            p.kill()
            p.join()


def start_starlette_app(builder, parms, port):

    kernel = builder(*parms)
    app = starlette_app_creator(kernel)
    uvicorn.run(app, host=LOCALHOST, port=port, log_level="debug")


