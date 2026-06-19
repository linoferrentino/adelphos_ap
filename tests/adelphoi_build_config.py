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



adelphos_simple_social_api_conf = {
       'cli_handler' : {
                'type' : 'standard_cli',
                },
       'kernel': {
                'type' : 'adelphos',
            },
       'social': {
           'type' : 'activity_pub',
            },
       'social_api' : {
           'type' : 'simple',
           },
        'social_gateway' : {
           'type' : 'activity_pub',
           },
        'social_dao' : {
           'type' : 'sqlite',
            },
        }



