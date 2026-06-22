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


from dataclasses import dataclass
from dataclasses import field


@dataclass
class SysCallPar:
    name: str
    required: bool
    def_value: str = None


@dataclass
class SysCall:

    name : str
    handler: callable
    pars: list[SysCallPar] = field(default_factory = list)

