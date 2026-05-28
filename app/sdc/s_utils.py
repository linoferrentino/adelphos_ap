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

import hashlib
import base64

from app.logging import gCon

from app.sdc.SimpleDependencyContainer import SimpleDependencyContainer
import app.sdc.Dependencies as dep

_conts = dict()


adelphos_standard_configuration = {
       'cli_handler' : {
                'type' : 'standard_cli',
                },
       'kernel': {
                'type' : 'adelphos',
            },
       'social': {
                'demo_users' : [ 'demo1', 'demo2' ]
            },
        'social_gateway' : {
           'type' : 'activity_pub',
           },
        }



def build_from(vhost):

    global _conts

    instance = vhost.instance_name
    config = vhost.config
    sdc = config.get('sdc')

    if sdc is None:
        gCon.log("Using standard configuration.")
        config['sdc'] = adelphos_standard_configuration

    hash_conf = base64.b64encode(hashlib.sha256(
        (instance + str(config)).encode('utf-8')).digest())

    cont = _conts.get(hash_conf)
    if cont is not None:
        return cont

    cont = SimpleDependencyContainer(vhost)

    _conts[hash_conf] = cont
    return cont



