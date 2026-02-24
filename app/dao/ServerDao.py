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

# the DataAccessObject for the Server table
# the Server here is synonymous for an ActivityPub server.

from app.dao.ServerDto import ServerDto
from app.dao.ServerDto import create_ap_server
from app.logging import gCon
from dataclasses import asdict
from app.dao.BaseDao import BaseDao


# the server dao has the logic to query and store activity pub servers
# this has to change name!
# It must become ApServerDao
class ServerDao(BaseDao):


    # I can set here the context.
    def __init__(self, dao):
        super().__init__(dao)
        self.table_name = "ap_server"


    # this function is only local: we do not create servers
    # around.
    def get_or_create_from_host_name(self, host_name):
        server_dto = self.get_from_hostname(host_name)

        if (server_dto is not None):
            return server_dto

        # at this point I have to create it.
        server_dto = create_ap_server(host_name)
        self.store(server_dto)
        gCon.log(f"I return {server_dto}")
        return server_dto



    def get_from_id(self, server_id):
        server_dto = self.dao.db.get_full_dto(self.table_name,
                        "server_id", server_id, ServerDto)
        return server_dto


    # also this function is local
    def get_from_hostname(self, host_name):
        server_dto = self.dao.db.get_full_dto(self.table_name,
                        "host_name", host_name, ServerDto)
        return server_dto


    def store_dict(self, server, server_as_dict):

        newid = self.dao.db.insert_dto_fields(self.table_name,
                            ('host_name',), server_as_dict)

        gCon.log(f"stored {server.host_name} his id {newid}")

        server.server_id = newid

