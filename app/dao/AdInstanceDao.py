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
from datetime import datetime
from app.consts import DAEMON_ID
from app.api.AdelphosException import AdelphosException
from app.api.AdelphosException import EAdelhposErrno
from app.dao.AdInstanceDto import AdInstanceDto
from app.dao.AdInstanceDto import AdInstancePack
from app.dao.AdInstanceDto import create_ad_instance
from ..logging import gCon

class AdInstanceDao(BaseDao):


    def __init__(self, dao):
        super().__init__(dao)
        self.table_name = "ad_instance"


    # No discover, returns the statu quo
    def is_instance_authorized(self, hostname):
        instance_pack = self.get_from_hostname(hostname)
        if instance_pack is None:
            return False
        return instance_pack.instance.authorized


    # no discover, it is not async!
    def get_from_hostname(self, host_name, maybe = True):
        ap_server_dto = self.dao.ap_server_dao.get_from_hostname(host_name)
        if (ap_server_dto is None):
            if maybe:
                return None
            raise AdelphosException(None, EAdelhposErrno.ENO_DAEMON_FOR_HOST)

        #gCon.log(f"Ok, the server {ap_server_dto} is present, is there a daemon actor?")

        # the name of the daemon is fixed.
        ap_actor_dto = self.dao.ap_actor_dao.get_from_preferred_username(
                ap_server_dto.server_id, DAEMON_ID)

        # this is a benign condition, the server is only a normal activity pub server.
        # but it could also host an adelphos instance, like the test one.
        if (ap_actor_dto is None):
            #gCon.log("No actor listening")
            if maybe:
                return None
            raise AdelphosException(None, EAdelhposErrno.ENO_DAEMON_FOR_HOST)

        # OK, now I can get the adelphos instance. If this fails it means that
        # I have registered the actor as only an activitypub daemon,
        ad_instance_dto = self.dao.db.get_full_dto(self.table_name,
                        'actor_fk', ap_actor_dto.actor_id, AdInstanceDto)
        
        if (ad_instance_dto is None):
            raise AdelphosException(f"No adelphos instance for {host_name}",
                                    EAdelhposErrno.ENO_DAEMON_FOR_HOST)

        #gCon.log(f"OK, there is already an adelphos instance {ad_instance_dto}")
        return AdInstancePack(ap_server_dto, ap_actor_dto, ad_instance_dto)


    async def discover_from_host_name(self, hostname):
        daemon_in_fediverse = f"@{DAEMON_ID}@{hostname}"
        #gCon.log(f"discovering actor {daemon_in_fediverse}")

        now_time = datetime.now()

        (daemon_server, daemon_actor) = await self.dao.app.ap_api.\
                get_or_discover_actor(daemon_in_fediverse)

        # If I am here without exceptions I can create the row in Db, the instance
        # is at first enabled.
        ad_instance_dto = create_ad_instance(daemon_actor.actor_id,
                                             1, f"discovered on {now_time}")
        self.dao.ad_instance_dao.store(ad_instance_dto)

        return AdInstancePack(daemon_server, daemon_actor, ad_instance_dto)


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

