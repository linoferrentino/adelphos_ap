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
# the starting point of the adelphos test

from contextlib import asynccontextmanager
import multiprocessing as mp
import contextlib
import uvicorn
from app.AdelphosApp import get_app

# inspired by 
# https://stackoverflow.com/questions/57412825/how-to-start-a-uvicorn-fastapi-in-background-when-testing-with-pytest
# and
# https://github.com/Kludex/uvicorn/issues/742#issuecomment-674411676


class ProcessServer:

    @contextlib.contextmanager
    def run_in_subprocess(self, instance_conf):
        mp.set_start_method('spawn')
        p = mp.Process(target = start_adelphos_conf, args = (instance_conf, ))
        p.start()
        try:
            yield
        finally:
            p.kill()
            p.join()


def start_adelphos_conf(adelphos_conf):
    remote1_app = get_app(adelphos_conf['General']['name'], None, adelphos_conf)
    uvicorn.run(remote1_app, host="127.0.0.1", port=int(adelphos_conf['General']['port']), 
                            log_level="info")


