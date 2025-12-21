# this file will load the configuration.



import tomllib
from .logging import gCon


def load_conf(instance_name: str):
    gCon.log(f"Loading configuration for {instance_name}")
