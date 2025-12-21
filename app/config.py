# this file will load the configuration.



import tomllib
from .logging import gCon
import os
from .logging import exit_err
import json


config = None


def load_conf(instance_name: str):
    global config

    toml_file = f"adelphos_ap_{instance_name}.toml"
    gCon.log(f"Loading configuration for {instance_name} file {toml_file}")

    if (os.path.exists(toml_file) == False):
        exit_err(f"Configuration file {toml_file} not found")

    with open(toml_file, "rb") as f:
        config = tomllib.load(f)

        gCon.log("This is my config")
        gCon.log(f"{json.dumps(config)}")
    

def get_config():
    global config
    return config


