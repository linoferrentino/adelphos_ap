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

from tests.testers.FdbSyncTester import FdbSyncTester
from tests.FederationTester import FederationTester


@pytest.fixture
def fdb1():

    db = MemoryStore()
    tester = FdbSyncTester()
    with tester.run_sync(db, LOCALHOST, my_test_schema_init):
        yield tester


@pytest.fixture
def fdb2():

    db = MemoryStore()
    tester = FdbSyncTester()
    with tester.run_sync(db, OTHERHOST, my_test_schema_init):
        yield tester


@pytest.fixture
def federation(fdb1, fdb2):

    federation = FederationTester()
    federation.add_hosts( (fdb1, fdb2) )
    with federation.do_playground():
        yield federation


def test_sync_fdbs(federation):

    response = federation.post_json(f'https://{LOCALHOST}/_backdoor_api_/login', 
                                    json = None)
    assert response.status_code == 202

