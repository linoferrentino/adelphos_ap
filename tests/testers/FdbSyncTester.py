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

import contextlib
from app.transport.SyncRouter import SyncRouter
from app.ap_api.ActivityPubMockup import ActivityPubMockup
from app.ap_api.ActivityPubMockup import ActivityPubMockupConfig
from app.federation.FederatedStore import FederatedStore


# this is the sync equivalent of AdelphosApp class
class FdbSyncTester(SyncRouter):


    def __init__(self):
        super().__init__()


    @contextlib.contextmanager
    def run_sync(self, db, host, schema_init):

        try:

            self.hostname = host

            config = ActivityPubMockupConfig(self, host)
            social = ActivityPubMockup(config)
            self.fdb = FederatedStore(host, db, social, schema_init)

            yield

        finally:

            db.close()

