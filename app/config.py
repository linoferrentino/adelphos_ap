# this file will load the configuration.



import tomllib
from .logging import gCon
import os
from .logging import exit_err
import json


def load_conf(instance_name, toml_file):

    if (toml_file is None):
        toml_file = f"adelphos_ap_{instance_name}.toml"

    gCon.log(f"Loading configuration file {toml_file}")

    if (os.path.exists(toml_file) == False):
        exit_err(f"Configuration file {toml_file} not found")

    with open(toml_file, "rb") as f:
        config = tomllib.load(f)

    gCon.rule("Read the configuration:")
    gCon.log(f"{json.dumps(config)}")

    return config
    

