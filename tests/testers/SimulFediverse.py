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
import tests.helpers.alias_helpers as ah
import tests.daemon.daemon_tests as dt

from app.sdc.Dependencies import Dependencies
from app.transport.bridge.loop import run_coro_in_loop
from app.core.algo.AliasAlgo import AliasAlgo


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

        - preferredusername: {root}
          name: Adelphos local root 
          login_shell: true


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
    instance_conf: object
    sock: object = None

    def mod(self, dependency):
        return self.instance.app.routable.get_dep(dependency)

    def kernel(self):
        return self.instance.app.get_kernel()


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
        instance_ob = fix._build_routable_config_impl(name,
            standard_simulated_instance_conf, instance, 'sync')
        si = SimulatedInstance(instance_ob, instance)
        self._inst[name] = si


    def _upgrade_sockets(self):
        for k, v in self._inst.items():
            gCon.log(f"instance {k} = {v.instance_conf}")
            ah.ws_local_root_login(v.instance, v.sock,
                                   v.instance_conf['root'],
                                   v.instance_conf['password'])


    def _do_accepts_instances(self):
        for k, v in self._inst.items():
            for k1, v1 in self._inst.items():
                if k == k1:
                    continue
                gCon.log(f"{k} accepts {k1} -> {v1.instance_conf['host']}")
                dt.ws_authorize_remote_adelphos(v.sock, v1.instance_conf['host'])


    def _do_setup_world(self, world_conf):
        world_setup = yaml.safe_load(world_conf)
        self._install_social_users(world_setup)
        self._install_aliases(world_setup)


    def _install_aliases(self, world_setup):
        self._for_all_configured_instances(world_setup,
              SimulFediverse._install_alias_for_instance)


    def _for_all_configured_instances(self, world_setup, action):
        for k, v in self._inst.items():
            inst_setup = world_setup.get(f"{k}_setup")
            if inst_setup is None:
                continue
            gCon.log(f"{k} -> instance {inst_setup}")
            action(v, inst_setup)


    def _install_social_users(self, world_setup):
        self._for_all_configured_instances(world_setup,
              SimulFediverse._install_users_for_instance)


    @staticmethod
    def _install_alias_for_instance(instance, inst_setup):
        families = inst_setup['families']
        for family in families:
            SimulFediverse._install_family(instance, family)


    @staticmethod
    def _install_family(instance, family):
        members = family['members']
        family_name = family['name']
        boss = family['boss']
        trust = family['trust']
        currency = family['currency']
        member = members[boss]
        actor_dto = SimulFediverse._get_actor_for_alias(instance, boss, member)

        gCon.log(f"boss {boss} is actor {actor_dto}")

        run_coro_in_loop(AliasAlgo.alias_create_safe, (instance.kernel(),
            actor_dto.act.actor_id, boss, family_name,
            member['password'], trust, currency))

        for member, m_dict in members.items():
            if member == boss:
                continue
            actor_dto = SimulFediverse._get_actor_for_alias(instance,
                        member, m_dict)
            gCon.log(f"Adding member {member} {m_dict} act {actor_dto}")

            run_coro_in_loop(AliasAlgo.family_add_alias_safe, (instance.kernel(),
                        actor_dto.act.actor_id, member, family_name,
                        m_dict['password']) )

    
    @staticmethod
    def _get_actor_for_alias(instance, alias, member):
        actor_dto = None
        if (actor := member.get('actor')) is not None:
            gCon.log(f"alias {alias} has actor {actor}")
            if actor[0] == '@':
                sg = instance.mod(Dependencies.SOCIAL_GATEWAY)
                gCon.log(f"social gateway {sg}")
                actor_dto = run_coro_in_loop(sg.discover_user, (actor,))
        else:
            actor = alias 

        if actor_dto is None:
            gCon.log(f"local alias {alias} has local actor {actor}")
            so = instance.mod(Dependencies.SOCIAL)
            inbox = so.local_user_get(actor)
            actor_dto = inbox.actor_dto

        return actor_dto


    @staticmethod
    def _install_users_for_instance(instance, inst_setup):
        users = inst_setup.get('users')
        if users is None:
            return
        for user in users:
            gCon.log(f"Create user {user}")
            ah.ws_create_user(instance.sock, user)


    def test(self, world_conf, testcase):
        list_inst = list( (k, x.instance) for k, x in self._inst.items() )
        with_stat = "with ("
        for ix in range(0, len(list_inst)):
            with_stat += f" list_inst[{ix}][1] as li_{ix},  "
        with_stat += " ):"
        with_stat += """
          with ("""
        for ix in range(0, len(list_inst)):
            with_stat += f" li_{ix}.websocket_connect(CNST.WS_ROUTE) as ws_{ix}, \n"

        with_stat += " ):"
        with_stat += """
            for ix in range(0, len(list_inst)):
                name_inst = list_inst[ix][0]
                self._inst[name_inst].sock = eval('ws_' + str(ix))

            self._upgrade_sockets()
            self._do_accepts_instances()

            #testcase.setup(self)
            self._do_setup_world(world_conf)
            testcase.pre_conditions()
            testcase.do_actions()
            testcase.verify()

        """
        gCon.log(f"The test to run is \n{with_stat}")
        exec(with_stat)
        
        gCon.log(f"Test done")

