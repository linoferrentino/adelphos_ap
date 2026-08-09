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
from app.logging import gCon
import app.sdc.standard_conf as sc


simulated_instance_conf = """

    general:

      debug: true 
      port: 8999
      host: {_host_} 
      root_path: /api
      root: ':local:{_root_handle_}'
      root_password: {_root_password_}

    social_dao:
      db_name: ':memory:'

"""


standard_simulated_instance_conf = (sc.testable_kernel_prefix
                + sc.common_adelphos_modules
                + sc.real_adelphos_chunk_modules 
                + simulated_instance_conf 
                + sc.testable_rpc_conf
                + sc.standard_cli_api
                + sc.debug_cli_api
                + sc.standard_inbox_api
                + sc.release_daemons)


class SimulFediverse:
    

    def __init__(self, fediverse_template, conf):
        if conf is not None:
            federated_world = fediverse_template.format(**conf)
        else:
            federated_world = fediverse_template

        fed_world = yaml.safe_load(federated_world)
        gCon.log(f"I have to build this world {fed_world}")

        for instance in fed_world['instances']:
            self._build_instance(instance)


    def _build_instance(self, instance):
        name = instance['name']
        gCon.log(f"Build instance {name} = {instance}")
        #routable = _build_routable_config_impl()
        pass






