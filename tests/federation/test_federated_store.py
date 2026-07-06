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


import pytest
from app.federation.FederatedStore import FederatedStore
from app.federation.FederatedStore import FdbException
from app.transport.SyncRouter import SyncRouter
from app.store.MemoryStore import MemoryStore
from app.store.SqliteStore import SqliteStore
from app.logging import gCon


from tests.federation.schema_simple import LOCALHOST, LOCALHOST1
from tests.federation.schema_simple import TYPE_T1, TYPE_T2
from tests.federation.schema_simple import FederatedUriTest
from app.sdc.Dependencies import Dependencies
from tests.federation.fixtures import fdb1_loc
from tests.federation.fixtures import federated_db_local


def test_new_object_f(fdb1_loc):

    t_id = fdb1_loc.begin_transaction()

    fields = {
            'key_int' : 99
            }

    fob1 = fdb1_loc.new_ob(t_id, TYPE_T1, "ob1", fields = fields)
    assert fob1 != None
    val_int = fob1().get_primitive_value('key_int')
    assert val_int == 99
    val_str = fob1().get_primitive_value('key_str')
    assert val_str is None
    val_int = fob1().get_primitive_value('int_none')
    assert val_int is None
    val_int = fob1().get_primitive_value('int_def')
    assert val_int == 101

    with pytest.raises(KeyError):
        val_str = fob1().get_primitive_value('key_str111')

    fdb1_loc.commit_transaction(t_id)

    assert fob1() is None

    t1uri = FederatedUriTest(TYPE_T1, 'ob1', host = LOCALHOST)
    t1uri_1 = FederatedUriTest(TYPE_T1, 'ob1', host = LOCALHOST1)
    t_id = fdb1_loc.begin_transaction()
    fob1 = fdb1_loc.uri_read_no_lock(t_id, t1uri)
    val_int = fob1().get_primitive_value('key_int')
    assert val_int == 99
    fob1 = fdb1_loc.uri_read_no_lock(t_id, t1uri_1)
    val_int = fob1().get_primitive_value('key_int')
    assert val_int == 99


@pytest.fixture
def fdb1_loc_a(fdb1_loc):

    t_id = fdb1_loc.begin_transaction()
    fob = fdb1_loc.new_ob(t_id, TYPE_T1, 'a', fields = {
        'key_int' : 11
        })
    fob().set_primitive_value('key1', 'val1')
    fdb1_loc.commit_transaction(t_id)
    return fdb1_loc


@pytest.fixture
def fdb1_link_a(fdb1_loc_a):

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t2uri = FederatedUriTest(TYPE_T2, 'a')
    t_id = fdb1_loc_a.begin_transaction()

    fob2 = fdb1_loc_a.new_ob(t_id, TYPE_T2, 'a')

    fob1 = fdb1_loc_a.uri_read_lock(t_id, t1uri)
    fob1().compare_and_swap_link('uses', None, fob2)
    fdb1_loc_a.commit_transaction(t_id)

    return fdb1_loc_a

 

def test_link2(fdb1_link_a):

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t2uri_old = FederatedUriTest(TYPE_T2, 'a')
    t2uri_new = FederatedUriTest(TYPE_T2, 'b')

    t_id = fdb1_link_a.begin_transaction()

    fob1 = fdb1_link_a.uri_read_lock(t_id, t1uri)
    fob2_old = fdb1_link_a.uri_read_lock(t_id, t2uri_old)
    fob2_new = fdb1_link_a.new_ob_uri(t_id, t2uri_new)
    fob1().compare_and_swap_link('uses', fob2_old, fob2_new)

    fdb1_link_a.commit_transaction(t_id)

    t_id = fdb1_link_a.begin_transaction()

    fob_get = fdb1_link_a.uri_read_no_lock(t_id, t2uri_old, True)
    assert fob_get == None

    fob_get = fdb1_link_a.uri_read_no_lock(t_id, t2uri_new)
    assert fob_get() != None
     

def test_link1_new(fdb1_link_a):

    t2uri = FederatedUriTest(TYPE_T2, 'a')
    t2urib = FederatedUriTest(TYPE_T2, 'b')

    t_id = fdb1_link_a.begin_transaction()

    fob_get = fdb1_link_a.uri_read_no_lock(t_id, t2uri)
    assert fob_get() != None
     
    fob_get = fdb1_link_a.uri_read_no_lock(t_id, t2urib, True)
    assert fob_get == None


def test_link1(fdb1_loc_a):

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t2uri = FederatedUriTest(TYPE_T2, 'a')
    t2urib = FederatedUriTest(TYPE_T2, 'b')
    t_id = fdb1_loc_a.begin_transaction()

    fob2 = fdb1_loc_a.new_ob_uri(t_id, t2uri)
    fob2_b = fdb1_loc_a.new_ob_uri(t_id, t2urib)
    fob1 = fdb1_loc_a.uri_read_lock(t_id, t1uri)
    fob1().compare_and_swap_link('uses', None, fob2)
    fdb1_loc_a.commit_transaction(t_id)

    t_id = fdb1_loc_a.begin_transaction()

    fob_get = fdb1_loc_a.uri_read_no_lock(t_id, t2uri)
    assert fob_get() != None
     
    fob_get = fdb1_loc_a.uri_read_no_lock(t_id, t2urib, True)
    assert fob_get == None


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
    fob = fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
        'key_int' : 1032
        })
    fob_get = fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob().uri == fob_get().uri


def test_set_uri_no_loc(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a', host = 'www.h2.com')
    t_id = fdb1_loc.begin_transaction()
    with pytest.raises(FdbException):
        fob = fdb1_loc.new_ob_uri(t_id, t1uri)


def test_create_alias(fdb1_loc):
    t1uri = FederatedUriTest('al', 'a')
    t_id = fdb1_loc.begin_transaction()
    with pytest.raises(FdbException) as fex:
        fob = fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
            'equity' : 99.2
            })
    gCon.log(f"exception {fex.value}")



def test_set_uri_local(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a')

    # test of a insert, no transaction no party
    fob = None
    with pytest.raises(FdbException):
        fob = fdb1_loc.new_ob_uri(None, t1uri )

    t_id = fdb1_loc.begin_transaction()
    fob = fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
        'key_int' : 391
        })

    fob_get = fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob().uri == fob_get().uri

