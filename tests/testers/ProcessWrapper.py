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

# Wrapper for a starlette application.

import pytest
from contextlib import asynccontextmanager
import multiprocessing as mp
import contextlib
import uvicorn
from app.transport.async_mode.StarletteHelper import starlette_app_creator
import time
from app.consts import API_POINT, LOCALHOST
from app.logging import gCon


class ProcessWrapper:

    @contextlib.contextmanager
    def run_in_subprocess(self, routable, parms, port):
        gCon.log(f"AO {routable}")
        p = mp.Process(target = start_starlette_app, args = (routable, parms, port))
        gCon.log("A1")
        p.start()
        gCon.log("A99")
        try:
            time.sleep(1)
            yield
            #time.sleep(1)
        finally:
            p.kill()
            p.join()


def start_starlette_app(aroutable, parms, port):

    gCon.log("AAAAAA START X")
    routable = aroutable(*parms)
    app = starlette_app_creator(routable)
    gCon.log("AAAAAA START")
    uvicorn.run(app, host=LOCALHOST, port=port, log_level="debug")


