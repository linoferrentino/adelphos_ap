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
from app.core.ui.MsgPresenter import MsgPresenter 
from app.logging import gCon


class MsgRawPresenter(MsgPresenter):

    def __init__(self, kernel):
        super().__init__(kernel)


    def _extract_msg_dict(self, msg_dict):
        return json.dumps(msg_dict)

