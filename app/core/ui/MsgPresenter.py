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


class MsgPresenter(Dependency):

    def __init__(self, kernel):
        super().__init__(kernel)


    def extract_msg_text(self, msg):
        if not isinstance(msg, dict):
            return str(msg)
        return self._extract_msg_dict(msg)


    @abstractmethod
    def _extract_msg_dict(self, msg_dict):
        pass

