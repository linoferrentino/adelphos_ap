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


from app.dao.ApServerDto import ApServerDto
from app.dao.ApServerDto import create_ap_server
from app.logging import gCon
from dataclasses import asdict
from app.dao.BaseDao import BaseDao


class ApServerDao(BaseDao):

    def __init__(self, db):
        super().__init__(db)
        self.table_name = "ap_server"


    def get_or_create_from_host_name(self, host_name):
        server_dto = self.get_from_hostname(host_name)

        if (server_dto is not None):
            return server_dto.server_id

        return self.create_from_hostname(host_name)


    def create_from_hostname(self, host_name):
        server_dto = create_ap_server(host_name)
        self.store(server_dto)
        return server_dto.server_id


    def get_or_create_from_uri(self, uri):
        return self.get_or_create_from_host_name(uri.netloc)


    def get_from_id(self, server_id):
        server_dto = self.db.get_full_dto(self.table_name,
                        "server_id", server_id, ApServerDto)
        return server_dto


    def get_from_hostname(self, host_name):
        server_dto = self.db.get_full_dto(self.table_name,
                        "host_name", host_name, ApServerDto)
        return server_dto


    def store_dict(self, server, server_as_dict):

        newid = self.db.insert_dto_fields(self.table_name,
                            ('host_name',), server_as_dict)
        server.server_id = newid


    def get_pk_name(self):
        return 'server_id'


    def get_table_name(self):
        return 'ap_server'


    def get_table_data_fields(self):
        return ('host_name', 'rpc_enabled')

