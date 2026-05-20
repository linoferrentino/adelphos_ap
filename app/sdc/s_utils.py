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
#from app.sdc.Dependencies import _conts
#from app.sdc.Dependencies import _active_cont
import app.sdc.Dependencies as dep

def build_from(vhost):
               # , *, social = None):
               #kernel = None,
               # cli_handler= None):
    #global _active_cont
    #global _conts

    instance = vhost.instance_name
    config = vhost.config
    hash_conf = base64.b64encode(hashlib.sha256(
        (instance + str(config)).encode('utf-8')).digest())

    #hash_conf = instance

    sdc = config.get('sdc')
    if sdc is None:
        raise Exception("Not found a dependency configuration")

    #cont = dep._conts.get(hash_conf)
    cont = dep._conts.get(hash_conf)
    if cont is not None:
        gCon.log(f"Found a stored container!instance {instance} {hash_conf}")
        dep._active_cont = cont
        return cont

    cont = SimpleDependencyContainer(vhost)
                                     #, social = social)
                                     #kernel = kernel)
                                     #, cli_handler = cli_handler)
    dep._active_cont = cont
    dep._conts[hash_conf] = cont
    gCon.log(f"config is {sdc} type {type(config)} {hash_conf}")
    return cont



