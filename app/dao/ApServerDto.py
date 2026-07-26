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


from dataclasses import dataclass
from app.dao.BaseDto import BaseDto


@dataclass
class ApServerDto(BaseDto):

    server_id: int

    host_name: str

    rpc_enabled: bool

    timestamp: str

    def get_pk(self):
        return self.server_id

    def get_pk_name(self):
        return 'server_id'


def create_ap_server(host_name):

    ap_server = ApServerDto(None, host_name, False, None)

    return ap_server



