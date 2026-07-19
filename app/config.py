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


import yaml
from .logging import gCon
import os
from .logging import exit_err
import json


CNF_GENERAL_SECTION = "general"
CNF_PRIVATE_KEY_FILE_KEY = "private_key"
CNF_HOST_KEY = "host"
CNF_PORT_KEY = "port"


class Config:

    def __init__(self, instance, config):
        self.instance = instance
        self.config = config


    def get_host(self):
        host = self.config['conf'][CNF_GENERAL_SECTION][CNF_HOST_KEY]
        return host


    def get_port(self):
        port = self.config['conf'][CNF_GENERAL_SECTION][CNF_PORT_KEY]
        return port


    def modules(self):
        return self.config['modules']


    def daemons_maybe(self):
        return self.config.get('daemons')


    def get_instance(self):
        return self.instance

    
    def get_social_config(self):
        return self.config['conf']['social']


    def get_social_dao_cnf(self):
        return self.config['conf']['social_dao']


    def get_conf(self, section):
        return self.config['conf'].get(section)


    def is_test_instance(self):
        return self.config['conf'][CNF_GENERAL_SECTION]['debug']


    def is_human_output(self):
        return self.config['conf'][CNF_GENERAL_SECTION].get('human_output',
                                                            True)


    def conf_mod(self, dependency):
        return self.config['conf'][dependency]


def load_conf(instance_name, yaml_file):

    if (yaml_file is None):
        yaml_file = f"adelphos_ap_{instance_name}.yaml"

    gCon.log(f"Loading configuration file {yaml_file}")

    if (os.path.exists(yaml_file) == False):
        exit_err(f"Configuration file {yaml_file} not found")

    with open(yaml_file, "rb") as f:
        config = yaml.safe_load(f)

    gCon.rule("Read the configuration:")
    gCon.log(f"{json.dumps(config)}")

    return config
    

