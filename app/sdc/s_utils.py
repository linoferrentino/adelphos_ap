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
from app.sdc.Kernel import Kernel
import app.sdc.Dependencies as dep


_kernels = dict()


def boot_kernel(instance, config, *, use_cache = True):

    global _kernels

    if use_cache == True:
        hash_conf = base64.b64encode(hashlib.sha256(
            (instance + str(config)).encode('utf-8')).digest())

        cont = _kernels.get(hash_conf)

        if cont is not None:
            gCon.log(f"[red]Returning already booted kernel {instance} {id(cont)}[/red]")
            return cont

    kern = Kernel(instance, config)
    gCon.log(f"[red]Booting kernel {instance} {id(kern)}[/red]")

    if use_cache == True:
        _kernels[hash_conf] = kern 

    return kern


def boot_new_kernel(instance, config):
    return boot_kernel(instance, config, use_cache = False)
