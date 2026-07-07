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


"""


common_adelphos_modules = """

    cli_handler:
      constructor: app.cli.StandardCliProvider.StandardCliProvider

    social_api:
      constructor: app.ad_api.adelphos.AdelphosApiProvider.AdelphosApiProvider


"""


real_adelphos_chunk_modules = """

    social_dao:
      constructor: app.federation.store.SqliteSocialDao.SqliteSocialDao
      priority: -100

    social_gateway:
      constructor: app.federation.ap.ActivityPubGateway.ActivityPubGateway


conf:


"""

testable_kernel_suffix_template = """

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


"""

syscalls_suffix = """

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
      alias:
        class: app.core.algo.AliasAlgo.AliasAlgo
        syscalls:
          - name: create
            handler: _sys_call_create
            pars:
                name:
                    required: true
                password:
                    required: true

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


release_kernel_template = (testable_kernel_prefix
                + common_adelphos_modules
                + real_adelphos_chunk_modules 
                + testable_kernel_suffix_template
                + syscalls_suffix)


release_kernel_conf = (testable_kernel_prefix
                + common_adelphos_modules
                + real_adelphos_chunk_modules 
                + syscalls_suffix)


