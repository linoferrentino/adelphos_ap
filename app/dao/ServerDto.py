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

# TODO create a string enumeration for the columns.


@dataclass
class ServerDto:

    # this only has not a default value.
    host_name: str

    server_id: int = None
    timestamp: str = None



