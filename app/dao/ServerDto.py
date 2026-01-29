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


from dataclasses import dataclass


@dataclass
class ServerDto:

    # this only has not a default value.
    host_name: str

    server_id: int = None
    timestamp: str = None


# the server dao has the logic to query and store servers
class ServerDao:

    # I can set here the context.
    def __init__(self, dao):
        self.dao = dao


    def get_from_hostname(self, host_name):

        table_name = "ap_server"

        fields_to_ask = ('host_name', 'server_id', 'timestamp')

        fields_to_seek = ('host_name', )
        values_to_seek = ( host_name, )

        dto = ctx.app.dao.get_dto_ex(table_name, fields_to_ask, 
                                     fields_to_seek, 
                            values_to_seek, ServerDto)
        return dto


    def store_server(self, server):
        pass
