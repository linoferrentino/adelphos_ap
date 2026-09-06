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

testable_rpcs = """
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

testable_rpc_conf = """

    rpc_api:

""" + testable_rpcs

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

          - name: return_no_mod
            pars:
              uri_str:
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
              alias:
                required: true
              password:
                required: true

          - name: add_alias
            pars:
              user:
                required: true
              alias:
                required: true
              password:
                required: true

          - name: alias_join_family
            pars:
              alias:
                required: true
              user:
                required: true
              family:
                required: true
              password:
                required: true

          - name: play_script
            pars:
              script_path:
                required: true

          - name: do_association
            pars:
              import_export_tax:
                par_type: float
                required: false
                default: 1.02
              family_dest:
                required: true
              family_source:
                required: true 
              upper_name:
                required: false
              location:
                required: false
              brotherhood_ratio:
                par_type: float
                required: false
                default: 0.9
              force:
                par_type: bool
                required: false
                default: false

      task:
        class: app.core.sys.TaskCalls.TaskCalls
        syscalls:

          - name: accept
            pars:
              task_id:
                required: true

          - name: decline
            pars:
              task_id:
                required: true


      object:
        class: app.core.sys.ObjectCalls.ObjectCalls
        syscalls:

          - name: put_ad
            pars:
              title:
                required: true
              description:
                required: false
              price:
                par_type: float
                required: true


      agora:
        class: app.core.sys.AgoraCalls.AgoraCalls
        syscalls:
          - name: list_ads
            pars:
              uplevel:
                par_type: int
                required: true
                validator: _v_ >= 0
              get_only_uri:
                par_type: bool
                required: false
                default: false

          - name: buy_object_idx
            pars:
              uplevel:
                par_type: int
                required: true
                validator: _v_ > 0
              index_ad:
                par_type: int
                required: true
                validator: _v_ >= 0
              dry_run:
                required: false
                par_type: bool
                default: true

          - name: received_pin
            pars:
              pin:
                par_type: int
                required: true
                validator: _v_ > 0


          - name: confirm_pin
            pars:
              pin:
                par_type: int
                required: true
                validator: _v_ > 0


          - name: buy_object_title
            pars:
              uplevel:
                par_type: int
                required: true
                validator: _v_ > 0
              ad_title:
                required: true
              dry_run:
                required: false
                par_type: bool
                default: true


      family:
        class: app.core.sys.FamilyCalls.FamilyCalls
        syscalls:
          - name: invite
            pars:
              invite_code:
                required: true
              user_handle:
                required: true

          - name: join
            pars:
              invite_code:
                required: true
              family_dest:
                required: true
              family_source:
                required: false

          - name: associate
            pars:
              import_export_tax:
                par_type: float
                required: true
              family_dest:
                required: true
              family_source:
                required: false
              upper_name:
                required: false
              location:
                required: false
              brotherhood_ratio:
                par_type: float
                required: false
                default: 0.9


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
                location:
                    required: false
                    default: no location given
 
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
                + federated_db_rpcs
                + testable_rpcs
                + standard_cli_api
                + debug_cli_api
                + standard_inbox_api
                + release_daemons)


release_kernel_conf = (release_kernel_prefix
                + common_adelphos_modules
                + real_adelphos_chunk_modules 
                + federated_db_rpcs
                + standard_cli_api 
                + standard_inbox_api
                + release_daemons)


