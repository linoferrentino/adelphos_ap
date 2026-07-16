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

from app.sdc.Dependencies import Dependencies

import app.sdc.standard_conf as stdcnf


testable_routable_kernel_template = """

modules:
    router:
      constructor: tests.transport.TRoutable.TRoutable
      args: 
        flag: {_flag_}

conf:
  general:
    debug: true

"""


federated_store_kernel_template = """

modules:

    fed_db:
      constructor: app.federation.FederatedStore.FederatedStore
      args: 
        schema:  {_inline_schema_}
        db_type: {_db_type_}

    router:
      constructor: app.AdelphosRouter.AdelphosRouter

conf:

    general:
      debug: true 
      host:  {_hostname_}
      api_point: null

    fed_db:
      db_name: ':memory:'
      db_type: mem
      

"""

adelphos_toy_1_conf = {

        '_port_': 7777,
        '_daemon_user_': 'test_kernel',
        '_demo_1_nick_': 't1',
        '_demo_1_complete_name_': 'demo user 1',
        '_demo_2_nick_': 't2',
        '_demo_2_complete_name_': 'demo user 2',
        '_root_handle_' : ':local:t1',
        '_root_password_' : 'super_secret',
}

adelphos_toy_2_conf = {

        '_port_': 9921,
        '_daemon_user_': 'test_kernel',
        '_demo_1_nick_': 't99',
        '_demo_1_complete_name_': 'demo user 99',
        '_demo_2_nick_': 't100',
        '_demo_2_complete_name_': 'demo user 100',
        '_root_handle_' : ':local:t99',
        '_root_password_' : 'super_secret',
}


adelphos_testable_1_conf = {

        '_port_': 7777,
        '_daemon_user_': 'adelphos',
        '_demo_1_nick_': 'demo1',
        '_demo_1_complete_name_': 'John Demo1',
        '_demo_2_nick_': 'demo2',
        '_demo_2_complete_name_': 'Mary Demo2',
        '_root_handle_' : ':local:demo1',
        '_root_password_' : 'tiger11',

}


adelphos_testable_2_conf = {

        '_port_': 9921,
        '_daemon_user_': 'adelphos',
        '_demo_1_nick_': 'demo77',
        '_demo_1_complete_name_': 'demo77 alt',
        '_demo_2_nick_': 'demo88',
        '_demo_2_complete_name_': 'demo88 alt',
        '_root_handle_' : ':local:demo77',
        '_root_password_' : 'tiger12',
}


debug_adelphos_chunk_modules = """

    social_dao:
      constructor: tests.testers.SimpleSocialDao.SimpleSocialDao
      priority: -100

    social_gateway:
      constructor: tests.testers.SimpleSocialGateway.SimpleSocialGateway

    backdoor_net:
      constructor: app.federation.BackdoorNet.BackdoorNet

conf:

"""


toy_common_adelphos_modules = """

    cli_handler:
      constructor: tests.testers.CliHandlerStub.CliHandlerStub

    social_api:
      constructor: tests.testers.SimpleSocialApiProvider.SimpleSocialApiProvider

"""

hybrid_common_adelphos_modules = """

    cli_handler:
      constructor: app.cli.StandardCliProvider.StandardCliProvider

    social_api:
      constructor: tests.testers.SimpleSocialApiProvider.SimpleSocialApiProvider


"""


toy_daemons = """

daemons:
  toy_init:
    constructor: tests.testers.ToyDaemon.ToyDaemon

"""


testable_toy_kernel_template = (stdcnf.testable_kernel_prefix
                + toy_common_adelphos_modules
                + debug_adelphos_chunk_modules 
                + stdcnf.testable_kernel_suffix_template
                + stdcnf.syscalls_suffix
                + toy_daemons)


testable_debug_kernel_template = (stdcnf.testable_kernel_prefix
                + stdcnf.common_adelphos_modules 
                + debug_adelphos_chunk_modules 
                + stdcnf.testable_kernel_suffix_template
                + stdcnf.syscalls_suffix)


testable_hybrid_kernel_template = (stdcnf.testable_kernel_prefix
                + hybrid_common_adelphos_modules 
                + debug_adelphos_chunk_modules 
                + stdcnf.testable_kernel_suffix_template
                + stdcnf.syscalls_suffix)



