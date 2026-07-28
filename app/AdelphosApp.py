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


import os
from app.logging import exit_err
from app.logging import gCon
from app.consts import ADELPHOS_AP_ENV_KEY
from app.config import load_conf
from app.transport.async_mode.StarletteHelper import starlette_app_creator
import app.sdc.s_utils as su
import yaml
import app.sdc.standard_conf as stdcnf

app = None

async def daemon_bg_cycle(app):

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


def get_app(instance_name = None, config_file = None, config = None):
    global app

    if (app is not None):
        return app

    if (instance_name is None):
        instance_name = os.getenv(ADELPHOS_AP_ENV_KEY)

    if (instance_name is None):
        exit_err(f"No instance given on command line and {ADELPHOS_AP_ENV_KEY} \
variable not defined")

    if ((config_file is not None) and (config is not None)):
        exit_err(f"You cannot set both config and config_file")

    if config is None:
        config = load_conf(instance_name, config_file)

    gCon.log(f"Starting adelphos instance {instance_name}")

    build_kernel = yaml.safe_load(stdcnf.release_kernel_conf)

    for key, val in config.items():
        if build_kernel['conf'].get(key) is not None:
            raise Exception("duplicate conf key in kernel configuration")
        gCon.log(f"Putting {key} = {val} in conf")
        build_kernel['conf'][key] = val

    kernel = su.boot_kernel(instance_name, build_kernel)

    app = starlette_app_creator(kernel)
    return app


