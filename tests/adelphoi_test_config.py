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


adelphos_simple_conf = {
       'cli_handler' : {
                'type' : 'standard_cli',
                },
       'kernel': {
                'type' : 'adelphos',
            },
       'social': {
                'demo_users' : [ 'demo1', 'demo2']
            }
        }


simple_tester_config = {
       'cli_handler' : {
                'type' : 'standard_cli',
                },
       'kernel': {
                'type' : 'test_kernel',
            },
       'social': {
                'demo_users' : [ 'demo1', 'demo2']
            }

        }


cli_stub_dep_conf = {
        'cli_handler' : {
                'type' : 'cli_stub',
                },
        'kernel': {
                'type' : 'test_kernel',
            },
       'social': {
                'demo_users' : [ 'demo1', 'demo2']
            }
        }


adelphos_stub =  {
        "General": {
    "debug": True, 
    "port": 7777, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:7777", 
    "root_user": ":local:", 
    # the password for alice is dual, one is for her being a normal alias in adelphos,
    # the other as a super user, the super user does not participate in the transactions
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users": [
    {"name": "alice99", "alias": "##alice.af", "password": "alice11", "root" : True}, 
    {"name": "bobzz", "alias": "##bob2.bf", "password": "bob22"}]
}



adelphos_t2_test =  {
    "General": {
    "debug": True, 
    "port": 9911, 
    "db_name": ":memory:", 
    "private_key": ":memory:", 
    "host":  "localhost:9911", 
    "root_user": ":local:", 
    # the password for alice is dual, one is for her being a normal alias in adelphos,
    # the other as a super user, the super user does not participate in the transactions
    "root_password": "$argon2id$v=19$m=65536,t=3,p=4$o/oGlKYis246QARUaT/0cw$7zu3oQuS1wz4Ddk/pc6NjLfTcac6YGmEX2VRGymtXrI"
    }, 
            "demo_users": [
    {"name": "alice99", "alias": "##alice.af", "password": "alice11", "root" : True}, 
    {"name": "bobzz", "alias": "##bob2.bf", "password": "bob22"}]
}


adelphos_remote2_conf  =  {"General": {
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


