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

from app.cli.CliPresenter import CliPresenter
from app.logging import gCon

class AdelphosSimplePresenter(CliPresenter):

    def __init__(self, kernel):
        super().__init__(kernel)


    def present_to_user_ok(self, sys_call_out):
        gCon.log(f"Transforming {sys_call_out}")
        return str(sys_call_out['res'])

