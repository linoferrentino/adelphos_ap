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

def build_from(vhost):

    global _conts

    instance = vhost.instance_name
    config = vhost.config
    hash_conf = base64.b64encode(hashlib.sha256(
        (instance + str(config)).encode('utf-8')).digest())


    sdc = config.get('sdc')
    if sdc is None:
        raise Exception("Not found a dependency configuration")

    cont = _conts.get(hash_conf)
    if cont is not None:
        #gCon.log(f"Found a stored container!instance {instance} {hash_conf}")
        return cont

    cont = SimpleDependencyContainer(vhost)

    _conts[hash_conf] = cont
    #gCon.log(f"config is {sdc} type {type(config)} {hash_conf}")
    return cont



