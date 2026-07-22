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
from app.core.AdelphosCoreException import AdelphosBaseException
from app.core.ECoreErrno import ECoreErrno
from app.logging import gCon


class RawPresenter(CliPresenter):

    def __init__(self, kernel):
        super().__init__(kernel)


    def present_to_user_ok(self, sys_call_out):
        sys_call_str = json.dumps(sys_call_out)
        gCon.log(f"....> exit >{sys_call_str}<")
        return sys_call_str


    def present_to_user_exc(self, exc):
        if isinstance(exc, AdelphosBaseException):
            dict_out = {
                    'errno' : exc.errno,
                    'errmsg' : exc.out_str,
            }
        else:
            dict_out = {
                    'errno' : ECoreErrno.ESYS,
                    'errmsg' : str(exc),
            }
        return json.dumps(dict_out)

