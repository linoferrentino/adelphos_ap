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
from app.federation.FederatedStore import FederatedStore
from app.federation.FederatedStore import FdbException
from app.transport.SyncRouter import SyncRouter
from app.store.MemoryStore import MemoryStore
# we have to test the federation without adelphos
#from app.dao.AdelphosUri import AdelphosUri
#from app.dao.AdelphosUri import EAdelphosType
from app.federation.FederatedObject import FederatedObject
from app.federation.FederatedUri import FederatedUri
from app.logging import gCon

# we have the transport and a federated db

# as long as they are unique we are fine.
TYPE_T1 = "TYPE_T1"
TYPE_T2 = "TYPE_T2"


class FederatedUriTest(FederatedUri):

    def unparse(self):
        base_name = "XX" + self.ob_type + "/" + self.name
        if self.family is not None:
            base_name += f"_f{self.family}"
        if self.host is not None:
            base_name += f"_f{self.host}"
        if self.fragment is not None:
            base_name += f"_f{self.fragment}"
        return base_name


# we test with these two objects
class FedeObClass1(FederatedObject):
    pass


class FedeObClass2(FederatedObject):
    pass


LOCALHOST = "www.h1.com"


@pytest.fixture
def fdb1_loc():

    db = MemoryStore()
    fdb = FederatedStore(LOCALHOST, db, None)
    return fdb


@pytest.fixture
def fdb1_loc_a(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t_id = fdb1_loc.begin_transaction()
    fob = fdb1_loc.create_uri(t_id, t1uri, 1)
    fob.set_primitive_value('key1', 'val1')
    fdb1_loc.commit_transaction(t_id)
    return fdb1_loc


def test_link1(fdb1_loc_a):

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t2uri = FederatedUriTest(TYPE_T2, 'a')
    t_id = fdb1_loc_a.begin_transaction()

    fob2 = fdb1_loc_a.create_uri(t_id, t2uri)
    fob1 = fdb1_loc_a.uri_read_lock(t_id, t1uri)
    #fob1().swap_link('uses', None, fob2)




def test_write_over_rollback(fdb1_loc_a):

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t_id = fdb1_loc_a.begin_transaction()
    fob_get = fdb1_loc_a.uri_read_lock(t_id, t1uri)
    val = fob_get().get_primitive_value('key1')
    assert val == 'val1'
    fob_get().set_primitive_value('key1', 'val1_new')
    val = fob_get().get_primitive_value('key1')
    assert val == 'val1_new'
    fdb1_loc_a.rollback_transaction(t_id)

    # this should not be possible
    with pytest.raises(AttributeError):
        fob_get().get_primitive_value('key1')

    t_id = fdb1_loc_a.begin_transaction()
    fob_get = fdb1_loc_a.uri_read_no_lock(t_id, t1uri)
    val = fob_get().get_primitive_value('key1')
    assert val == 'val1'
    

def test_after_transaction(fdb1_loc_a):

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t_id = fdb1_loc_a.begin_transaction()
    fob_get = fdb1_loc_a.uri_read_no_lock(t_id, t1uri)
    val = fob_get().get_primitive_value('key1')
    assert val == 'val1'
    assert t1uri == fob_get().uri


def test_set_uri_local_1(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a', host = LOCALHOST)
    t_id = fdb1_loc.begin_transaction()
    fob = fdb1_loc.create_uri(t_id, t1uri, 1)
    fob_get = fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob.uri == fob_get().uri


def test_set_uri_no_loc(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a', host = 'www.h2.com')
    t_id = fdb1_loc.begin_transaction()
    with pytest.raises(FdbException):
        fob = fdb1_loc.create_uri(t_id, t1uri, 1)


def test_set_uri_local(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a')

    # test of a insert, no transaction no party
    fob = None
    with pytest.raises(FdbException):
        fob = fdb1_loc.create_uri(None, t1uri, 1)

    t_id = fdb1_loc.begin_transaction()
    fob = fdb1_loc.create_uri(t_id, t1uri, 1)

    # the object survives a garbage collect, because it has a reference
    # count of one and it is in the transaction set.
    #fdb1_loc.gc()

    fob_get = fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob.uri == fob_get().uri

