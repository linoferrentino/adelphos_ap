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

"""

adelphos_toy_1_conf = {

        '_port_': 7777,
        '_daemon_user_': 'test_kernel',
        '_demo_1_nick_': 't1',
        '_demo_1_complete_name_': 'demo user 1',
        '_demo_2_nick_': 't2',
        '_demo_2_complete_name_': 'demo user 2',
}

adelphos_toy_2_conf = {

        '_port_': 9921,
        '_daemon_user_': 'test_kernel',
        '_demo_1_nick_': 't99',
        '_demo_1_complete_name_': 'demo user 99',
        '_demo_2_nick_': 't100',
        '_demo_2_complete_name_': 'demo user 100',
}


adelphos_testable_1_conf = {

        '_port_': 7777,
        '_daemon_user_': 'adelphos',
        '_demo_1_nick_': 'demo1',
        '_demo_1_complete_name_': 'John Demo1',
        '_demo_2_nick_': 'demo2',
        '_demo_2_complete_name_': 'Mary Demo2',
}


adelphos_testable_2_conf = {

        '_port_': 9921,
        '_daemon_user_': 'adelphos',
        '_demo_1_nick_': 'demo77',
        '_demo_1_complete_name_': 'demo77 alt',
        '_demo_2_nick_': 'demo88',
        '_demo_2_complete_name_': 'demo88 alt',
}


real_adelphos_chunk_modules = """

    social_dao:
      constructor: app.federation.store.SqliteSocialDao.SqliteSocialDao
      priority: -100

    social_gateway:
      constructor: app.federation.ap.ActivityPubGateway.ActivityPubGateway


"""

debug_adelphos_chunk_modules = """

    social_dao:
      constructor: tests.testers.SimpleSocialDao.SimpleSocialDao
      priority: -100

    social_gateway:
      constructor: tests.testers.SimpleSocialGateway.SimpleSocialGateway

    backdoor_net:
      constructor: app.federation.BackdoorNet.BackdoorNet


"""


common_adelphos_modules = """

    cli_handler:
      constructor: app.cli.StandardCliProvider.StandardCliProvider

    social_api:
      constructor: app.ad_api.adelphos.AdelphosApiProvider.AdelphosApiProvider


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


testable_kernel_prefix = """

modules:

    router:
      constructor: app.AdelphosRouter.AdelphosRouter

    social:
      constructor: app.federation.BaseSocial.BaseSocial

    social_net:
      constructor: app.federation.ap.ActivityPubNetwork.ActivityPubNetwork

    cli_net:
      constructor: app.cli.AdelphosCliRouter.AdelphosCliRouter

"""


testable_kernel_suffix = """

    rpc_api:
      constructor: app.core.sys.SysCallGateway.SysCallGateway
      args:
        realm: rpc_api

    inbox_api:
      constructor: app.core.sys.SysCallGateway.SysCallGateway
      args:
        realm: inbox_api

    cli_api:
      constructor: app.core.sys.SysCallGateway.SysCallGateway
      args:
        realm: cli_api

conf:

    general:

      debug: true 
      port: {_port_}
      host: localhost:{_port_} 
      api_point: null

    social_dao:
      db_name: ':memory:'

    social:
      users:

        - preferredusername: {_daemon_user_}
          name: Adelphos daemon
          login_shell: false

        - preferredusername: {_demo_1_nick_}
          name: {_demo_1_complete_name_} 
          login_shell: true

        - preferredusername: {_demo_2_nick_}
          name: {_demo_2_complete_name_}
          login_shell: true


    rpc_api:
        math:
            class: tests.testers.MathRPCs.MathRPCs
            syscalls:
                - name: radd
                  pars:
                    n1:
                      required: true
                    n2:
                      required: true

    cli_api:
      dbg:
          class: app.core.sys.DebugModule.DebugModule
          syscalls:
            - name: echo
              pars:
                msg:
                  required: true
            - name: sndpost
              pars:
                from:
                  required: true
                to:
                  required: true
                msg:
                  required: true

            - name: radd
              pars:
                host:
                  required: true
                n1:
                  required: true
                n2:
                  required: true

    inbox_api:
      sapi:
          class: app.ad_api.BaseSocialApiProvider.BaseSocialApiProvider
          syscalls:

            - name: q
              handler: _sys_call_q
              pars: 
                api_id: 
                  required: true
                payload:
                  required: true

            - name: a
              handler: _sys_call_a
              pars:
                api_id:
                  required: true
                payload:
                  required: true


"""


testable_toy_kernel_template = (testable_kernel_prefix
                + toy_common_adelphos_modules
                + debug_adelphos_chunk_modules + testable_kernel_suffix)


testable_debug_kernel_template = (testable_kernel_prefix
                + common_adelphos_modules 
                + debug_adelphos_chunk_modules + testable_kernel_suffix)


testable_hybrid_kernel_template = (testable_kernel_prefix
                + hybrid_common_adelphos_modules 
                + debug_adelphos_chunk_modules + testable_kernel_suffix)


testable_release_kernel_template = (testable_kernel_prefix
                + common_adelphos_modules
                + real_adelphos_chunk_modules + testable_kernel_suffix)


