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


    def get_dep(self, dep):
        return self.vhost.get_dep(dep)


    @property 
    def kernel(self):
        return self.vhost


    def conf(self):
        return self.vhost.conf()

