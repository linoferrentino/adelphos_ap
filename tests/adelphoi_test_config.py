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


social_dao_test_conf = {
        "db_name" : ":memory:"
        }


social_test_kernel = {"users" : [
    {"preferredusername" : "test_kernel", 'name': 'test daemon', 'login_shell' : False},
    {"preferredusername" : "t1", 'name' : "demo user 1", 'login_shell' : True},
    {"preferredusername" : "t2", 'name' : "demo user 2", 'login_shell' : True},
                ]}


social_test_kernel2 = {"users" : [
    {"preferredusername" : "test_kernel", 'name': 'test daemon', 'login_shell' : False},
    {"preferredusername" : "t99", 'name' : "demo user 1", 'login_shell' : True},
    {"preferredusername" : "t100", 'name' : "demo user 2", 'login_shell' : True},
                ]}



test_social_cnf = {"users" : [
    {"preferredusername" : "adelphos", 'name': 'Adelphos daemon', 'login_shell' : False},
    {"preferredusername" : "demo1", 'name' : "John demo1", 'login_shell' : True},
    {"preferredusername" : "demo2", 'name' : "Mary demo2", 'login_shell' : True},
                ]}


test_social2_cnf = {"users" : [
    {"preferredusername" : "adelphos", 'name': 'Adelphos daemon', 'login_shell' : False},
    {"preferredusername" : "demo77", 'name' : "demo77 alt", 'login_shell' : True},
    {"preferredusername" : "demo88", 'name' : "demo88 alt", 'login_shell' : True},
                ]}



simple_testable_kernel = {
        'modules' : [  {
                    'name' : Dependencies.ROUTER,
                    'constructor' : 'app.AdelphosRouter.AdelphosRouter',
                },
                {
                    'name' : Dependencies.CLI_HANDLER,
                    'constructor' : 'app.cli.StandardCliProvider.StandardCliProvider',
                },
                {
                    'name' : Dependencies.SOCIAL,
                    'constructor' : 'app.federation.BaseSocial.BaseSocial',
                },
                {
                    'name' : Dependencies.SOCIAL_NET,
                    'constructor' : 'app.federation.ap.ActivityPubNetwork.ActivityPubNetwork',
                },
                {
                    'name' : Dependencies.CLI_NET,
                    'constructor' : 'app.cli.AdelphosCliRouter.AdelphosCliRouter',
                },
                {
                    'name' : Dependencies.SOCIAL_DAO,
                    'constructor' : 'tests.testers.SimpleSocialDao.SimpleSocialDao',
                },
                {
                    'name' : Dependencies.SOCIAL_GATEWAY,
                    'constructor' : 'tests.testers.SimpleSocialGateway.SimpleSocialGateway',
                },
                {
                    'name' : Dependencies.BACKDOOR_NET,
                    'constructor' : 'app.federation.BackdoorNet.BackdoorNet',
                },
                {
                    'name' : Dependencies.SOCIAL_API,
                    'constructor' : 'app.ad_api.adelphos.AdelphosApiProvider.AdelphosApiProvider',
                },
                {
                    'name' : Dependencies.RPC_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'rpc_providers' ],
                },
                {
                    'name' : Dependencies.INBOX_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'inbox_providers' ],
                },
                {
                    'name' : Dependencies.CLI_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'cli_providers' ],
                },
        ],
}

cli_stub_dep_conf = {
        'cli_handler' : {
                'type' : 'cli_stub',
                },
        'kernel': {
                'type' : 'test_kernel',
            },
       'social': {
           #'type' : 'simple',
            },
        'social_api' : {
           'type' : 'simple'
           },
       'social_gateway' : {
           'type' : 'simple',
           },
        'social_dao' : {
           'type' : 'simple',
            },
        }


toy_testable_kernel = {
        'modules' : [  {
                    'name' : Dependencies.ROUTER,
                    'constructor' : 'app.AdelphosRouter.AdelphosRouter',
                },
                {
                    'name' : Dependencies.CLI_HANDLER,
                    'constructor' : 'tests.testers.CliHandlerStub.CliHandlerStub',
                },
                {
                    'name' : Dependencies.SOCIAL,
                    'constructor' : 'app.federation.BaseSocial.BaseSocial',
                },
                {
                    'name' : Dependencies.SOCIAL_NET,
                    'constructor' : 'app.federation.ap.ActivityPubNetwork.ActivityPubNetwork',
                },
                {
                    'name' : Dependencies.CLI_NET,
                    'constructor' : 'app.cli.AdelphosCliRouter.AdelphosCliRouter',
                },
                {
                    'name' : Dependencies.SOCIAL_DAO,
                    'constructor' : 'tests.testers.SimpleSocialDao.SimpleSocialDao',
                },
                {
                    'name' : Dependencies.SOCIAL_GATEWAY,
                    'constructor' : 'tests.testers.SimpleSocialGateway.SimpleSocialGateway',
                },
                {
                    'name' : Dependencies.BACKDOOR_NET,
                    'constructor' : 'app.federation.BackdoorNet.BackdoorNet',
                },
                {
                    'name' : Dependencies.SOCIAL_API,
                    'constructor' : 'tests.testers.SimpleSocialApiProvider.SimpleSocialApiProvider',
                },
                {
                    'name' : Dependencies.RPC_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'rpc_providers' ],
                },
                {
                    'name' : Dependencies.INBOX_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'inbox_providers' ],
                },
                {
                    'name' : Dependencies.CLI_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'cli_providers' ],
                },
        ],
}




adelphos_simple_conf_deprecated = {
       'cli_handler' : {
                'type' : 'standard_cli',
                },
       'kernel': {
                'type' : 'adelphos',
            },
       'social': {
           #'type' : 'simple',
            },
       'social_api' : {
           'type' : 'adelphos'
           },
        'social_gateway' : {
           'type' : 'simple',
           },
        'social_dao' : {
           'type' : 'simple',
            },

        }



medium_testable_kernel = {
        'modules' : [  {
                    'name' : Dependencies.ROUTER,
                    'constructor' : 'app.AdelphosRouter.AdelphosRouter',
                },
                {
                    'name' : Dependencies.CLI_HANDLER,
                    'constructor' : 'app.cli.StandardCliProvider.StandardCliProvider',
                },
                {
                    'name' : Dependencies.SOCIAL,
                    'constructor' : 'app.federation.BaseSocial.BaseSocial',
                },
                {
                    'name' : Dependencies.SOCIAL_NET,
                    'constructor' : 'app.federation.ap.ActivityPubNetwork.ActivityPubNetwork',
                },
                {
                    'name' : Dependencies.CLI_NET,
                    'constructor' : 'app.cli.AdelphosCliRouter.AdelphosCliRouter',
                },
                {
                    'name' : Dependencies.SOCIAL_DAO,
                    'constructor' : 'tests.testers.SimpleSocialDao.SimpleSocialDao',
                },
                {
                    'name' : Dependencies.SOCIAL_GATEWAY,
                    'constructor' : 'tests.testers.SimpleSocialGateway.SimpleSocialGateway',
                },
                {
                    'name' : Dependencies.BACKDOOR_NET,
                    'constructor' : 'app.federation.BackdoorNet.BackdoorNet',
                },
                {
                    'name' : Dependencies.SOCIAL_API,
                    'constructor' : 'tests.testers.SimpleSocialApiProvider.SimpleSocialApiProvider',
                },
                {
                    'name' : Dependencies.RPC_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'rpc_providers' ],
                },
                {
                    'name' : Dependencies.INBOX_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'inbox_providers' ],
                },
                {
                    'name' : Dependencies.CLI_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'cli_providers' ],
                },
        ],
}


simple_tester_config = {
       'cli_handler' : {
                'type' : 'standard_cli',
                },
       'kernel': {
                'type' : 'test_kernel',
            },
       'social': {
           #'type' : 'simple',
            },
        'social_api' : {
           'type' : 'simple'
           },
        'social_gateway' : {
           'type' : 'simple',
           },
        'social_dao' : {
           'type' : 'simple',
            },
        }




debug_syscalls = {
        'dbg' : {
            'class' : 'app.core.sys.DebugModule.DebugModule',
            'syscalls' : [
                { 'name' : 'echo',
                  'pars' : {
                      'msg' : {
                          'required' : True,
                          }
                      }

                 },
                {
                  'name' : 'sndpost',
                  'pars' : {
                      'from' : {
                          'required' : True,
                       },
                      'to' : {
                          'required' : True,
                      },
                      'msg': {
                          'required' : True,
                      }
                  }
                },
                {
                    'name' : 'radd',
                    'pars' : {
                        'host' : {
                            'required' : True,
                        },
                        'n1' : {
                            'required' : True,
                        },
                        'n2' : {
                            'required' : True,
                        }
                    }
                },
                ]
            }
        }


remote_syscalls = {
        'math' : {
            'class' : 'tests.testers.MathRPCs.MathRPCs',
            'syscalls' : [ {
                'name' : 'radd',
                'pars' : {
                    'n1' : {
                        'required' : True,
                        },
                    'n2' : {
                        'required' : True,
                        },
                    }
                } ]
            }
        }


inbox_syscalls = {
        'sapi' : {
            'class' : 'app.ad_api.BaseSocialApiProvider.BaseSocialApiProvider',
            'syscalls' : [ {
                'name' : 'q',
                'handler' : '_sys_call_q',
                'pars' : {
                    'api_id' : {
                            'required' : True,
                        },
                    'payload' : {
                            'required' : True,
                        },
                    },
                },
                {
                'name' : 'a',
                'handler' : '_sys_call_a',
                'pars' : {
                    'api_id' : {
                            'required' : True,
                        },
                    'payload' : {
                            'required' : True,
                        }
                    }
                } ]
            }
        }


simple_testable_conf = {
        "General": {
            "debug": True, 
            "port": 7777, 
            "host":  "localhost:7777",
        },
        "social_dao" : social_dao_test_conf,
        "social" : test_social_cnf,
        "rpc_providers" : remote_syscalls, 
        "cli_providers" : debug_syscalls,
        'inbox_providers' : inbox_syscalls,
}


simple_toy_conf = {
        "General": {
            "debug": True, 
            "port": 7777, 
            "host":  "localhost:7777",
        },
        "social_dao" : social_dao_test_conf,
        "social" : social_test_kernel,
        "rpc_providers" : remote_syscalls, 
        "cli_providers" : debug_syscalls,
        'inbox_providers' : inbox_syscalls,
}


simple_toy_conf_2 = {
        "General": {
            "debug": True, 
            "port": 9921, 
            "host":  "localhost:9921",
        },
        "social_dao" : social_dao_test_conf,
        "social" : social_test_kernel2,
        "rpc_providers" : remote_syscalls, 
        "cli_providers" : debug_syscalls,
        'inbox_providers' : inbox_syscalls,
}


simple_testable_conf_2 =  {
        "General": {
             "debug": True, 
             "port": 9921, 
             "host":  "localhost:9921", 
        },
        "social_dao" : social_dao_test_conf,
        "social" : test_social2_cnf,
        "rpc_providers" : remote_syscalls,
        "cli_providers" : debug_syscalls,
        'inbox_providers' : inbox_syscalls,
    }





adelphos_stub_deprecated =  {
        "conf" : {
            "social_dao" : social_dao_test_conf,
            "social" : test_social_cnf,
            "rpc_providers" : remote_syscalls, 
            "cli_providers" : debug_syscalls,
            'inbox_providers' : inbox_syscalls,
            },
        "General": {
    "debug": True, 
    "port": 7777, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:7777", 
    "root_user": ":local:", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users": [
    {"name": "alice99", "alias": "##alice.af", "password": "alice11", "root" : True}, 
    {"name": "bobzz", "alias": "##bob2.bf", "password": "bob22"}]
}


routable_test_kernel =  {
        "conf" : {
            "social_dao" : social_dao_test_conf,
            "social" :  social_test_kernel,
            "rpc_providers" : remote_syscalls,
            "cli_providers" : debug_syscalls,
            'inbox_providers' : inbox_syscalls,
            },
        "General": {
    "debug": True, 
    "port": 7777, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:7777", 
    "root_user": ":local:", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users": [
    {"name": "alice99", "alias": "##alice.af", "password": "alice11", "root" : True}, 
    {"name": "bobzz", "alias": "##bob2.bf", "password": "bob22"}]
}


adelphos_t1_test = {
       "General": {
            "debug": True, 
            "port": 9919, 
            "host":  "localhost:9919", 
        },
       "social_dao" : social_dao_test_conf,
       "social" : test_social_cnf,
       "rpc_providers" : remote_syscalls,
       "cli_providers" : debug_syscalls,
       'inbox_providers' : inbox_syscalls,

    }


adelphos_t1_test_deprecated =  {
        "conf" : {
            "social_dao" : social_dao_test_conf,
            "social" : test_social2_cnf,
            "rpc_providers" : remote_syscalls,
            "cli_providers" : debug_syscalls,
            'inbox_providers' : inbox_syscalls,
            },
    "General": {
    "debug": True, 
    "port": 9919, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9919", 
    "root_user": ":local:", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }
}


adelphos_t2_test =  {
    "General": {
        "debug": True, 
        "port": 9921, 
        "host":  "localhost:9921", 
    },
    "social_dao" : social_dao_test_conf,
    "social" : test_social2_cnf,
    "rpc_providers" : remote_syscalls,
    "cli_providers" : debug_syscalls,
    'inbox_providers' : inbox_syscalls,
}


adelphos_t2_test_deprecated =  {
        "conf" : {
            "social_dao" : social_dao_test_conf,
            "social" : test_social2_cnf,
            "rpc_providers" : remote_syscalls,
            "cli_providers" : debug_syscalls,
            'inbox_providers' : inbox_syscalls,
            },
    "General": {
    "debug": True, 
    "port": 9921, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9921", 
    "root_user": ":local:", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }
}


routable_test2_kernel =  {
        "conf" : {
            "social_dao" : social_dao_test_conf,
            "social" : social_test_kernel2,
            "rpc_providers" : remote_syscalls,
            "cli_providers" : debug_syscalls,
            'inbox_providers' : inbox_syscalls,
            },
    "General": {
    "debug": True, 
    "port": 9921, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9921", 
    "root_user": ":local:", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }
}


adelphos_remote2_conf  =  {
        "conf" : {
            "social_dao" : social_dao_test_conf,
            "social" : test_social_cnf,
            'inbox_syscalls' : inbox_syscalls,
            },
        "General": {
    "debug": True, 
    "port": 5011, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:5011", 
    "root_user": "@john_test@localhost:5011", 
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$Odkr3o7V+SOVF6Dn5NB8XQ$NX9ZG6tqB4a/hQqEM6hvNnFsJt5VvCjbwuvYEU00f60"
    }, 
            "demo_users":
   [{"name": "john_test", "alias": "##john.jf", "password": "john11"}, 
    {"name": "mary_test", "alias": "##mary.mf", "password": "mary11"}]
}


test_routable_kernel = {
        'modules' : [  {
                'name' : Dependencies.ROUTER,
                'constructor' : "tests.transport.TRoutable.TRoutable",
                'args' : [ 'flag1', ],
                },
        ],
        'conf' : {
            'General' : {
                'debug' : True,
            },
        }
}

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

adelphos_testable_1_conf = {

        '_port_': 7777,
        '_demo_1_nick_': 'demo1',
        '_demo_1_complete_name_': 'John Demo1',
        '_demo_2_nick_': 'demo2',
        '_demo_2_complete_name_': 'Mary Demo2',
}


adelphos_testable_2_conf = {

        '_port_': 9921,
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

    rcp_api:
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

        - preferredusername: adelphos
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

testable_debug_kernel_template = (testable_kernel_prefix
                + common_adelphos_modules 
                + debug_adelphos_chunk_modules + testable_kernel_suffix)


testable_release_kernel_template = (testable_kernel_prefix
                + common_adelphos_modules
                + real_adelphos_chunk_modules + testable_kernel_suffix)


simple_testable_conf = {
        "General": {
            "debug": True, 
            "port": 7777, 
            "host":  "localhost:7777",
        },
        "social_dao" : social_dao_test_conf,
        "social" : test_social_cnf,
        "rpc_providers" : remote_syscalls, 
        "cli_providers" : debug_syscalls,
        'inbox_providers' : inbox_syscalls,
}

