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
from app.sdc.standard_conf import adelphos_standard_configuration


_conts = dict()


def build_kernel(instance, config):

    global _conts

    hash_conf = base64.b64encode(hashlib.sha256(
        (instance + str(config)).encode('utf-8')).digest())

    cont = _conts.get(hash_conf)
    if cont is not None:
        gCon.log(f"[red]Returning container {id(cont)}[/red]")
        return cont

    cont = SimpleDependencyContainer(instance, config)
    #gCon.log(f"[red]Creating container {id(cont)}[/red]")

    _conts[hash_conf] = cont
    return cont


def boot_new_kernel(instance, config):
    cont = SimpleDependencyContainer(instance, config)
    return cont
