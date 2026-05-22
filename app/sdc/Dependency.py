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

from abc import ABC, abstractmethod

class Dependency(ABC):

    def __init__(self, vhost):
        self.vhost = vhost

