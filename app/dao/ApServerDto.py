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
#

# the DataTransferObject for the Server table
# the Server here is synonymous for an ActivityPub server.


from ..logging import gCon
from dataclasses import dataclass
from app.dao.BaseDto import BaseDto
from typing import NamedTuple


# the fields are in the same order as the database
@dataclass
class ApServerDto(BaseDto):

    server_id: int

    host_name: str

    timestamp: str

    def get_pk(self):
        return self.server_id


#class ApServerPack(NamedTuple):
#
#    ob: ApServerDto


# this function will create an Activity Pub Server objecct.
def create_ap_server(host_name):

    ap_server = ApServerDto(None, host_name, None)

    return ap_server



