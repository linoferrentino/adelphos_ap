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
from app.federation.LifespanAware import LifespanAware
from app.sdc.Dependency import Dependency


class Kernel(Dependency, LifespanAware):

    def __init__(self, vhost):
        super().__init__(vhost)


    @abstractmethod
    def get_syscalls(self):
        pass


