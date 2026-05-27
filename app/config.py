# this file will load the configuration.



import tomllib
from .logging import gCon
import os
from .logging import exit_err
import json


CNF_GENERAL_SECTION = "General"
CNF_PRIVATE_KEY_FILE_KEY = "private_key"
CNF_HOST_KEY = "host"


class Config:

    def __init__(self, instance, config):
        self.instance = instance
        self.config = config


    def get_host(self):
        host = self.config[CNF_GENERAL_SECTION][CNF_HOST_KEY]
        return host


    def get_instance(self):
        return self.instance

    
    def get_social_config(self):
        return self.config['sdc']['social']


    def get_social_gw_config(self):
        return self.config['sdc']['social_gateway']



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
    

