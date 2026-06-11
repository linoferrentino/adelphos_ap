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


class SysCallModule(ABC):

    def __init__(self, kernel, sys_prefix):
        self.kernel = kernel
        self.sys_prefix = sys_prefix


    @abstractmethod
    def get_syscalls(self):
        pass


