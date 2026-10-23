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
import pprint
import app.misc.utils as utils


class AdelphosSimplePresenter(CliPresenter):

    def __init__(self, kernel):
        super().__init__(kernel)


    def present_to_user_ok(self, sys_call_out):
        res = sys_call_out['res']
        #gCon.log(f"Transforming {res} type {type(res)}")
        ##return str(sys_call_out['res'])
        if isinstance(res, str):
            return res
        resp = pprint.pformat(res, indent = 4, width = 60)
        gCon.log(f"will return {resp}")
        resp_html = utils.str_to_html_msg(resp)
        return resp_html

