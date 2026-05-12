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
# the main entry point for the Activity Pub implementation of adelphos.


import typer
import uvicorn

from typer import Option
from typing_extensions import Annotated

from app.consts import ADELPHOS_AP_ENV_KEY
from app.consts import LOCALHOST
from app.consts import API_POINT
from app.AdelphosApp import get_app
from app.logging import gCon


#def main_OLD(
#        instance_name:
#Annotated[str, Option( help = f"Name of Adelphos instance, default env var \
#{ADELPHOS_AP_ENV_KEY}")] = None,
#        config_file:
#Annotated[str, Option( help = "Config file to use, default: adelphos_ap_${instance_name}.toml")] = None
#        ):
#
#    app = get_app(instance_name, config_file, None)
#    port = app.config['General']['port']
#    gCon.log(f"Will start {instance_name} on port {port}")
#    uvicorn.run(app, host="127.0.0.1", port=port, reload=False)


def main(
  instance_name:
Annotated[str, Option( help = f"Name of Adelphos instance, default env var \
{ADELPHOS_AP_ENV_KEY}")] = None,
        config_file:
Annotated[str, Option( help = "Config file to use, default: adelphos_ap_${instance_name}.toml")] = None
        ):
    app = get_app(instance_name, config_file, None)
    config = app.get_config()
    port = config['General']['port']
    gCon.log(f"Starting instance {instance_name} on port {port}")
    uvicorn.run(app, host=LOCALHOST, port=port, reload=False, 
                log_level = "info")


if __name__ == "__main__":
    typer.run(main)
