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

adelphos_t1_test =  {
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


