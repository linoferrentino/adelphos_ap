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
# This is the Adelphos instance. A Host which can talk
# to other adelphos instances in the fediverse.

from app.dao.BaseDao import BaseDao
from app.consts import DAEMON_ID
from app.api.AdelphosException import AdelphosException
from app.api.AdelphosException import EAdelhposErrno
from app.dao.AdInstanceDto import AdInstanceDto
from ..logging import gCon

class AdInstanceDao(BaseDao):


    def __init__(self, dao):
        super().__init__(dao)
        self.table_name = "ad_instance"


    # this function does not try to create it.
    def get_from_hostname(self, host_name):
        ap_server_dto = self.dao.ap_server_dao.get_from_hostname(host_name)
        if (ap_server_dto is None):
            return None

        gCon.log(f"Ok, the server {ap_server_dto} is present, is there a daemon actor?")

        # the name of the daemon is fixed.
        ap_actor_dto = self.dao.ap_actor_dao.get_from_preferred_username(
                ap_server_dto.server_id, DAEMON_ID)

        if (ap_actor_dto is None):
            # this may happen if the server is an activity pub but not an adelphos instance
            # for now I raise an error, this is something that should not happen
            raise AdelphosException(f"The server {host_name} is a normal activity \
pub server", EAdelhposErrno.ERR_NO_DAEMON_FOR_HOST)

        # OK, now I can get the adelphos instance, and this MUST succeed, because
        # otherwise it means that I have a daemon actor pending.
        ad_instance_dto = self.dao.db.get_full_dto(self.table_name,
                        'actor_fk', ap_actor_dto.actor_id, AdInstanceDto)
        
        if (ad_instance_dto is None):
            raise AdelphosException(f"Database corrupt? No instance for {host_name}")

        gCon.log(f"OK, there is already an adelphos instance {ad_instance_dto}")
        return ad_instance_dto


    def store_dict(self, instance, instance_as_dict):
        self.dao.db.insert_dto_fields(self.table_name, 
                ('actor_fk', 'authorized', 'comment'), instance_as_dict)
        # I have a forced primary key
        return instance_as_dict['actor_fk']


    # gets the name of the column that stores the private key.
    def get_pk_name(self):
        return 'actor_fk'


    # We have a table name for each DAO (at least once)
    def get_table_name(self):
        return 'ad_instance'

