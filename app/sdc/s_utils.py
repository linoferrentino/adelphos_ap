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


_conts = dict()
_active_cont = None


def build_from(config, *,
                social = None, 
                kernel = None,
                cli_handler= None):

    global _active_cont

    hash_conf = base64.b64encode(hashlib.sha256(
        str(config).encode('utf-8')).digest())

    sdc = config.get('sdc')
    if sdc is None:
        return

    cont = _conts.get(hash_conf)
    if cont is not None:
        gCon.log("Found a stored container!")
        _active_cont = cont
        return

    cont = SimpleDependencyContainer(config, social = social,
                                     kernel = kernel, cli_handler = cli_handler)
    _active_cont = cont
    _conts[hash_conf] = cont
    gCon.log(f"config is {sdc} type {type(config)} {hash_conf}")


def get_dep(dep):

    return None
