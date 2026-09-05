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

import json
from app.cli.CliPresenter import CliPresenter
from app.logging import gCon


class RawPresenter(CliPresenter):

    def __init__(self, kernel):
        super().__init__(kernel)


    def present_to_user_ok(self, sys_call_out):
        gCon.log(f"Sys_call_out {sys_call_out}")
        match sys_call_out['context']:
            case 'math' | 'sapi' | 'alias' | 'fdb' :
                return sys_call_out
            case _:
                sys_call_str = json.dumps(sys_call_out)
                return sys_call_str


