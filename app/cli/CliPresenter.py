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
from app.sdc.Dependency import Dependency


class CliPresenter(Dependency):

    def __init__(self, kernel):
        super().__init__(kernel)


    @abstractmethod
    def present_to_user_ok(self, sys_call_out):
        pass


    @abstractmethod
    def present_to_user_exc(self, exc):
        pass
