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
class SocialRPC:

    name: str
    class_instance: object
    required_pars: list = field(default_factory = list)

