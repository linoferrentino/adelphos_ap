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


common_kernel_prefix = """

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

testable_kernel_prefix = common_kernel_prefix + """
    cli_presenter:
      constructor: tests.testers.RawPresenter.RawPresenter

"""

release_kernel_prefix = common_kernel_prefix + """
    cli_presenter:
      constructor: app.cli.AdelphosSimplePresenter.AdelphosSimplePresenter

"""

common_adelphos_modules = """

    cli_handler:
      constructor: app.cli.StandardCliProvider.StandardCliProvider

    social_api:
      constructor: app.ad_api.adelphos.AdelphosApiProvider.AdelphosApiProvider

    fed_db:
      constructor: app.core.model.AdelphosFederatedStore.AdelphosFederatedStore
     

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
      root_path: /api
      root: {_root_handle_}
      root_password: {_root_password_}

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

release_daemons = """
    
daemons:
        
  init:
    constructor: app.core.AdelphosInitDaemon.AdelphosInitDaemon


"""

testable_rpc_conf = """

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

"""

federated_db_rpcs = """

    rpc_api:
      fdb:
        class: app.federation.FederatedRPCs.FederatedRPCs
        syscalls:
          - name: borrow
            pars:
              uri_str:
                required: true
              lock:
                required: true

          - name: return
            pars:
              uri_str:
                required: true
              obstr:
                required: true




"""

standard_cli_api = """

    cli_api:

      root:
        class: app.core.sys.RootApi.RootApi
        syscalls:
          - name: deny_remote
            pars:
              host:
                required: true

          - name: allow_remote
            pars:
              host:
                required: true

          - name: push_alias
            pars:
              alias:
                required: true

          - name: pop_alias

          - name: add_user
            pars:
              user:
                required: true
 
          - name: add_user_alias
            pars:
              user:
                required: true
              trust:
                required: false
                default: 50.0
                par_type: float
              alias:
                required: true
              password:
                required: true
              currency:
                required: false
                default: EUR


      trustline:
        class: app.core.sys.TrustLineCalls.TrustLineCalls
        syscalls:
          - name: create
            pars:
              alias_to:
                required: true
              trust:
                par_type: float
                required: true
              maximum_weight:
                par_type: float
                required: false
                default: 5.0
              maximum_dim:
                par_type: float
                required: false
                default: 50.0
              change_ratio:
                par_type: float
                required: false
                default: 1.0
              

      family:
        class: app.core.sys.FamilyCalls.FamilyCalls
        syscalls:
          - name: invite
            pars:
              invite_code:
                required: true
              user_handle:
                required: true


      alias:
        class: app.core.sys.AliasCalls.AliasCalls
        syscalls:

          - name: whoami

          - name: logout

          - name: login
            pars:
              login:
                required: true
              password:
                required: true

          - name: put_token
            pars:
              tk:
                required: true

          - name: send_msg
            pars:
              alias:
                required: true
              msg:
                required: true

"""

debug_cli_api = """

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

"""

social_api = """

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


standard_inbox_api = """

    inbox_api:
      alias:
        class: app.core.algo.AliasAlgo.AliasAlgo
        syscalls:
          - name: create
            pars:
                name:
                    required: true
                password:
                    required: true
                trust:
                    required: false 
                    par_type: float
                    default: 25.0 
                currency:
                    required: false 
                    default: EUR
 
          - name: join_family
            pars:
                alias:
                    required: true
                family:
                    required: true
                invite_code:
                    required: true
                password:
                    required: true""" + social_api




release_kernel_template = (testable_kernel_prefix
                + common_adelphos_modules
                + real_adelphos_chunk_modules 
                + testable_kernel_suffix_template
                + testable_rpc_conf
                + standard_cli_api
                + debug_cli_api
                + standard_inbox_api
                + release_daemons)


release_kernel_conf = (release_kernel_prefix
                + common_adelphos_modules
                + real_adelphos_chunk_modules 
                + standard_cli_api 
                + standard_inbox_api
                + release_daemons)


