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

import pytest

# test two federated stores communicating with sync interface.
from tests.federation.schema_simple import LOCALHOST, LOCALHOST1, OTHERHOST
from tests.federation.schema_simple import TYPE_T1, TYPE_T2
from tests.federation.schema_simple import FederatedUriTest
from tests.federation.schema_simple import my_test_schema_init


from app.store.MemoryStore import MemoryStore

#from tests.testers.FdbSyncTester import FdbSyncTester
#from tests.FederationTester import FederationTester


@pytest.fixture
def fdbt1():

    db = MemoryStore()
    tester = FdbSyncTester()
    with tester.run_sync(db, LOCALHOST, my_test_schema_init):
        yield tester


@pytest.fixture
def fdbt2():

    db = MemoryStore()
    tester = FdbSyncTester()
    with tester.run_sync(db, OTHERHOST, my_test_schema_init):
        yield tester


#@pytest.fixture
#def federation(fdbt1, fdbt2):
#
#    federation = FederationTester()
#    federation.add_hosts( (fdbt1, fdbt2) )
#    with federation.do_playground():
#        yield federation


def x_test_sync_fdbs(fdbt1, fdbt2, federation):

    fdb1 = fdbt1.fdb

    t_id = fdb1.begin_transaction()

    fields = {
            'key_int' : 99
            }

    fob1 = fdb1.new_ob(t_id, TYPE_T1, "ob1", fields = fields)

    uri_1 = fob1().uri

    fdb1.commit_transaction(t_id)

    fdb2 = fdbt2.fdb

    t_id = fdb2.begin_transaction()

    uri_1.host = LOCALHOST

    fob1 = fdb2.uri_read_no_lock(t_id, uri_1)

    val_int = fob1().get_primitive_value('key_int')

    assert val_int == 99


