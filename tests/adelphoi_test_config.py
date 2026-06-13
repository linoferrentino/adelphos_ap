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

social_dao_test_conf = {
        "db_name" : ":memory:"
        }



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



adelphos_simple_conf = {
       'cli_handler' : {
                'type' : 'standard_cli',
                },
       'kernel': {
                'type' : 'adelphos',
            },
       'social': {
           #'type' : 'simple',
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
       'social_gateway' : {
           'type' : 'simple',
           },
        'social_dao' : {
           'type' : 'simple',
            },
        }


adelphos_stub =  {
        "conf" : {
            "social_dao" : social_dao_test_conf,
            "social" : test_social_cnf
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
            "social" : test_social2_cnf
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
            "social" : test_social2_cnf
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
            "social" : test_social_cnf
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


