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

# Wrapper for a starlette application.

import pytest
from contextlib import asynccontextmanager
import multiprocessing as mp
import contextlib
import uvicorn
#from app.transport.async_mode.AsyncTransport import AsyncTransport
#from app.transport.async_mode.AsyncGateway import AsyncGateway
#from app.transport.async_mode.StarletteWrap import StarletteWrap
from app.transport.async_mode.StarletteHelper import starlette_app_creator
#from app.transport.Routable import async_lifespan_gw
import time
from app.consts import API_POINT, LOCALHOST


class ProcessWrapper:

    @contextlib.contextmanager
    def run_in_subprocess(self, routable, port):
        p = mp.Process(target = start_starlette_app, args = (routable, port))
        p.start()
        try:
            time.sleep(1)
            yield
        finally:
            p.kill()
            p.join()


def start_starlette_app(aroutable, port):

    routable = aroutable("flag")
    #transport = AsyncTransport()
    #app = StarletteWrap(transport = transport, routable = routable, 
    #                lifespan = async_lifespan_gw)
    app = starlette_app_creator(routable)
    uvicorn.run(app, host=LOCALHOST, port=port, log_level="debug", root_path=API_POINT)


