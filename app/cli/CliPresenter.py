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
from abc import ABC, abstractmethod
from app.sdc.Dependency import Dependency
from app.core.AdelphosCoreException import AdelphosBaseException
from app.core.ECoreErrno import ECoreErrno


class CliPresenter(Dependency):

    def __init__(self, kernel):
        super().__init__(kernel)


    @abstractmethod
    def present_to_user_ok(self, sys_call_out):
        pass


    def present_to_user_exc(self, exc):
        if isinstance(exc, AdelphosBaseException):
            dict_out = {
                    'errno' : exc.errno,
                    'res' : exc.out_str,
            }
        else:
            dict_out = {
                    'errno' : ECoreErrno.ESYS,
                    'res' : str(exc),
            }
        #return json.dumps(dict_out)
        return dict_out

