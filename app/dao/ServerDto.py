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


# the server dao has the logic to query and store servers
class ServerDao:


    # I can set here the context.
    def __init__(self, dao):
        self.dao = dao
        self.table_name = "ap_server"


    # this function is only local: we do not create servers
    # around.
    def get_or_create_from_host_name(self, ctx, host_name):
        server_dto = self.get_from_hostname(ctx, host_name)

        if (server_dto is not None):
            return server_dto

        # at this point I have to create it.
        server_dto = ServerDto(host_name)
        self.store(ctx, server_dto)
        gCon.log(f"I return {server_dto}")
        return server_dto


    def get_from_hostname(self, ctx, host_name):

        fields_to_ask = ('host_name', 'server_id', 'timestamp')

        fields_to_seek = ('host_name', )
        values_to_seek = ( host_name, )

        dto = ctx.app.dao.get_dto_ex(self.table_name, fields_to_ask, 
                                     fields_to_seek, 
                            values_to_seek, ServerDto)
        return dto


    def store(self, ctx, server):

        fields_stored = {
                         'host_name': server.host_name,
                         }

        newid = self.dao.insert_dto(ctx, self.table_name, fields_stored)

        gCon.log(f"stored {server.host_name} his id {newid}")

        server.server_id = newid

