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

# this is the sync equivalent of AdelphosApp class
class FdbSyncTester(SyncRouter):


    def __init__(self):
        super().__init__()


    @contextlib.contextmanager
    def run_sync(self, db, host, schema_init):

        try:

            social = ActivityPubMockup(config, True, self)
            fdb = FederatedStore(host, db, social, schema_init)

            yield fdb 

        finally:

            db.close()

