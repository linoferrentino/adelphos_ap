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
from dataclasses import dataclass

from app.logging import gCon
import app.consts as CNST

import app.sdc.standard_conf as sc
import tests.testers.fixtures as fix


simulated_instance_conf = """

    general:

      debug: true 
      port: 8999
      host: {host} 
      root_path: /api
      root: ':local:{root}'
      root_password: {password}

    social:
      users:
        - preferredusername: adelphos
          name: Adelphos daemon
          login_shell: false


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


@dataclass
class SimulatedInstance:

    instance: object
    sock: object = None


class SimulFediverse:
    

    def __init__(self, fediverse_template, conf):
        if conf is not None:
            federated_world = fediverse_template.format(**conf)
        else:
            federated_world = fediverse_template

        fed_world = yaml.safe_load(federated_world)
        gCon.log(f"I have to build this world {fed_world}")

        self._inst = dict()
        for instance in fed_world['instances']:
            self._build_instance(instance)


    def _build_instance(self, instance):
        name = instance['name']
        gCon.log(f"Build instance {name} = {instance}")
        instance = fix._build_routable_config_impl(name,
            standard_simulated_instance_conf, instance, 'sync')
        si = SimulatedInstance(instance)
        self._inst[name] = si


    def test(self, testcase):
        list_inst = list( x.instance for x in self._inst.values() )
        gCon.log(f"I have to test the list {list_inst}")
        with_stat = "with ("
        for ix in range(0, len(list_inst)):
            with_stat += f" list_inst[{ix}] as li_{ix},  "
        with_stat += " ):"
        with_stat += """
          with ("""
        for ix in range(0, len(list_inst)):
            with_stat += f" li_{ix}.websocket_connect(CNST.WS_ROUTE) as ws_{ix}, \n"

        with_stat += " ):"
        with_stat += """
            gCon.log("Hello")
        """
        gCon.log(f"The test to run is \n{with_stat}")
        exec(with_stat)


