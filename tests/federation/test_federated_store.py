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
import re
from app.federation.FederatedStore import FederatedStore
from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors
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
from app.transport.bridge.loop import run_coro_in_loop


def test_new_object_f(fdb1_loc):

    run_coro_in_loop(a_test_new_object_f, (fdb1_loc,))


async def a_test_new_object_f(fdb1_loc):

    t_id = await fdb1_loc.begin_transaction()

    fields = {
            'key_int' : 99
            }

    fob1 = await fdb1_loc.new_ob(t_id, TYPE_T1, "ob1", fields = fields)
    assert fob1() is not None
    val_int = fob1().get_scalar('key_int')
    assert val_int == 99
    val_str = fob1().get_scalar('key_str')
    assert val_str is None
    val_int = fob1().get_scalar('int_none')
    assert val_int is None
    val_int = fob1().get_scalar('int_def')
    assert val_int == 101

    with pytest.raises(FdbException) as fex:
        #with pytest.raises(KeyError) as fex:
        val_str = fob1().get_scalar('key_str111')
    assert fex.value.errno == EFdbErrors.EFDB_UNKNOWN_COLUMN
    del fex

    await fdb1_loc.commit_transaction(t_id)

    assert fob1() is None

    t1uri = FederatedUriTest(TYPE_T1, 'ob1', host = LOCALHOST)
    t1uri_1 = FederatedUriTest(TYPE_T1, 'ob1', host = LOCALHOST1)
    t_id = await fdb1_loc.begin_transaction()
    fob1 = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    val_int = fob1().get_scalar('key_int')
    assert val_int == 99
    fob1 = await fdb1_loc.uri_read_no_lock(t_id, t1uri_1)
    val_int = fob1().get_scalar('key_int')
    assert val_int == 99

    with pytest.raises(FdbException) as fex:
        fob1().set_scalar('key_int', 33)
    assert fex.value.errno == EFdbErrors.EFDB_NO_LOCK_ON_OB


async def a_fdb1_loc_a(fdb1_loc):

    t_id = await fdb1_loc.begin_transaction()
    fob = await fdb1_loc.new_ob(t_id, TYPE_T1, 'a', fields = {
        'key_int' : 11
        })
    fob().set_scalar('key1', 'val1')
    await fdb1_loc.commit_transaction(t_id)


async def a_fdb1_link_a(fdb1_loc):

    await a_fdb1_loc_a(fdb1_loc)

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t2uri = FederatedUriTest(TYPE_T2, 'a')
    t_id = await fdb1_loc.begin_transaction()

    fob2 = await fdb1_loc.new_ob(t_id, TYPE_T2, 'a')

    fob1 = await fdb1_loc.uri_read_lock(t_id, t1uri)
    fob1().compare_and_swap_link('uses', None, fob2)

    await fdb1_loc.commit_transaction(t_id)
 

def test_link2(fdb1_loc):

    run_coro_in_loop(a_test_link2, (fdb1_loc,))


async def a_test_link2(fdb1_loc):

    await a_fdb1_link_a(fdb1_loc)

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t2uri_old = FederatedUriTest(TYPE_T2, 'a')
    t2uri_new = FederatedUriTest(TYPE_T2, 'b')

    t_id = await fdb1_loc.begin_transaction()

    fob1 = await fdb1_loc.uri_read_lock(t_id, t1uri)
    fob2_old = await fdb1_loc.uri_read_lock(t_id, t2uri_old)
    fob2_new = await fdb1_loc.new_ob_uri(t_id, t2uri_new)
    fob1().compare_and_swap_link('uses', fob2_old, fob2_new)

    await fdb1_loc.commit_transaction(t_id)

    t_id = await fdb1_loc.begin_transaction()

    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t2uri_old, True)
    assert fob_get == None

    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t2uri_new)
    assert fob_get() != None
     

def test_link1_new(fdb1_loc):

    run_coro_in_loop(a_test_link1_new, (fdb1_loc,))


async def a_test_link1_new(fdb1_loc):

    await a_fdb1_link_a(fdb1_loc)

    t2uri = FederatedUriTest(TYPE_T2, 'a')
    t2urib = FederatedUriTest(TYPE_T2, 'b')

    t_id = await fdb1_loc.begin_transaction()

    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t2uri)
    assert fob_get() != None
     
    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t2urib, True)
    assert fob_get == None


def test_link1(fdb1_loc):
    run_coro_in_loop(a_test_link1, (fdb1_loc,))


async def a_test_link1(fdb1_loc):

    await a_fdb1_loc_a(fdb1_loc)

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t2uri = FederatedUriTest(TYPE_T2, 'a')
    t2urib = FederatedUriTest(TYPE_T2, 'b')
    t_id = await fdb1_loc.begin_transaction()

    fob2 = await fdb1_loc.new_ob_uri(t_id, t2uri)
    fob2_b = await fdb1_loc.new_ob_uri(t_id, t2urib)
    fob1 = await fdb1_loc.uri_read_lock(t_id, t1uri)
    fob1().compare_and_swap_link('uses', None, fob2)
    await fdb1_loc.commit_transaction(t_id)

    t_id = await fdb1_loc.begin_transaction()

    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t2uri)
    assert fob_get() != None
     
    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t2urib, True)
    assert fob_get == None


def test_write_over_rollback(fdb1_loc):
    run_coro_in_loop(a_test_write_over_rollback, (fdb1_loc,))


async def a_test_write_over_rollback(fdb1_loc):

    await a_fdb1_loc_a(fdb1_loc)

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t_id = await fdb1_loc.begin_transaction()
    fob_get = await fdb1_loc.uri_read_lock(t_id, t1uri)
    val = fob_get().get_scalar('key1')
    assert val == 'val1'
    fob_get().set_scalar('key1', 'val1_new')
    val = fob_get().get_scalar('key1')
    assert val == 'val1_new'
    await fdb1_loc.rollback_transaction(t_id)

    # this should not be possible
    with pytest.raises(AttributeError):
        fob_get().get_scalar('key1')

    t_id = await fdb1_loc.begin_transaction()
    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    val = fob_get().get_scalar('key1')
    assert val == 'val1'
    

def test_after_transaction(fdb1_loc):

    run_coro_in_loop(a_test_after_transaction, (fdb1_loc,))


async def a_test_after_transaction(fdb1_loc):

    await a_fdb1_loc_a(fdb1_loc)

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t_id = await fdb1_loc.begin_transaction()
    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    val = fob_get().get_scalar('key1')
    assert val == 'val1'
    assert t1uri == fob_get().uri


def test_set_uri_local_1(fdb1_loc):

    run_coro_in_loop(a_test_set_uri_local_1, (fdb1_loc,))


async def a_test_set_uri_local_1(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a', host = LOCALHOST)
    t_id = await fdb1_loc.begin_transaction()
    fob = await fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
        'key_int' : 1032
        })
    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob().uri == fob_get().uri


def test_set_uri_no_loc(fdb1_loc):
    run_coro_in_loop(a_test_set_uri_no_loc, (fdb1_loc, ))


async def a_test_set_uri_no_loc(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a', host = 'www.h2.com')
    t_id = await fdb1_loc.begin_transaction()
    with pytest.raises(FdbException):
        fob = await fdb1_loc.new_ob_uri(t_id, t1uri)


def test_create_alias(fdb1_loc):
    run_coro_in_loop(a_test_create_alias, (fdb1_loc,))


async def a_test_create_alias(fdb1_loc):
    t1uri = FederatedUriTest('al', 'a')
    t_id = await fdb1_loc.begin_transaction()

    with pytest.raises(FdbException) as fex:
        fob = await fdb1_loc.new_ob_uri(t_id, t1uri)

    assert fex.value.errno == EFdbErrors.EFDB_REQUIRED_FIELD_MISSING

    fob = await fdb1_loc.new_ob_uri(t_id, t1uri, fields = { 'equity' : 99.2 })

    assert fob().get_scalar('equity') == 99.2


def test_uri_set(fdb1_loc):
    run_coro_in_loop(a_test_uri_set, (fdb1_loc,))


async def a_test_uri_set(fdb1_loc):
    t1uri = FederatedUriTest('t_uri_set', 'tj1')
    t_id = await fdb1_loc.begin_transaction()
    fob = await fdb1_loc.new_ob_uri(t_id, t1uri)

    with pytest.raises(FdbException) as fex:
        await fdb1_loc.commit_transaction(t_id)

    assert fex.value.errno == EFdbErrors.EFDB_REQUIRED_FIELD_MISSING

    tmember_uri = FederatedUriTest('t_member', 'member_lino', host = LOCALHOST)
    fob_dep = await fdb1_loc.new_ob_uri(t_id, tmember_uri, fields = {
        'name' : 'lino'
        })
    
    with pytest.raises(FdbException) as fex:
        fob().set_link('members', fob_dep)
    assert fex.value.errno == EFdbErrors.EFDB_SCALAR_UNEXPECTED

    with pytest.raises(FdbException) as fex:
        await fdb1_loc.commit_transaction(t_id)
    assert fex.value.errno == EFdbErrors.EFDB_REQUIRED_FIELD_MISSING
    assert re.search('members$', fex.value.out_str)

    fob().add_link('members', fob_dep)

    await fdb1_loc.commit_transaction(t_id)

    t_id = await fdb1_loc.begin_transaction()

    fob = await fdb1_loc.uri_read_no_lock(t_id, tmember_uri)
    assert fob() is not None
    assert fob().get_scalar('name') == 'lino'

    fob_set = await fdb1_loc.uri_read_no_lock(t_id, t1uri)

    with pytest.raises(FdbException) as fex:
        set_members = fob_set().get_scalar('members')
    assert fex.value.errno == EFdbErrors.EFDB_SCALAR_EXPECTED

    set_members = fob_set().get_set('members')
    assert len(set_members) == 1
    member = list(set_members)[0]
    gCon.log(f"Deleting uri {member} from {set_members}")

    uri_ob = FederatedUriTest.parse(member)

    fob_member = await fdb1_loc.uri_read_no_lock(t_id, uri_ob)
    assert fob_member() is not None

    set_members = fob_set().get_set('members')
    assert len(set_members) == 1
 
    with pytest.raises(FdbException) as fex:
        fob_set().remove_set('members', fob_member)
    assert fex.value.errno == EFdbErrors.EFDB_NO_LOCK_ON_OB

    set_members = fob_set().get_set('members')
    assert len(set_members) == 1

    fob_lock = await fdb1_loc.uri_read_lock(t_id, uri_ob)
    assert fob_lock() is not None
    assert fob_lock() != fob_member()

    fob_set_lock = await fdb1_loc.uri_read_lock(t_id, t1uri)

    fob_set_lock().remove_set('members', fob_lock)

    with pytest.raises(FdbException) as fex:
        await fdb1_loc.commit_transaction(t_id)
    assert fex.value.errno == EFdbErrors.EFDB_CARDINALITY_LOWER

    
def test_json_field(fdb1_loc):
    run_coro_in_loop(a_test_json_field, (fdb1_loc,))


async def a_test_json_field(fdb1_loc):

    t1uri = FederatedUriTest('t_json', 'tj1')
    t_id = await fdb1_loc.begin_transaction()
    obj = {
            'a' : 19,
            'b' : 'some_val'
            }

    with pytest.raises(FdbException) as fex:
        fob = await fdb1_loc.new_ob_uri(t_id, t1uri)
    assert fex.value.errno == EFdbErrors.EFDB_REQUIRED_FIELD_MISSING

    fob = await fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
        'ob_json' : obj
        })

    obj_get = fob().get_scalar('ob_json')
    assert id(obj_get) == id(obj)

    fob().add_ref()

    await fdb1_loc.commit_transaction(t_id)
    t_id = await fdb1_loc.begin_transaction()
    fob = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob() is not None

    obj_get = fob().get_scalar('ob_json')
    assert obj_get == obj
    assert obj_get['a'] == 19

    obj = {
            'b' : 99
      }

    with pytest.raises(FdbException) as fex:
        await fob().set_scalar('ob_json', obj)
    assert fex.value.errno == EFdbErrors.EFDB_NO_LOCK_ON_OB


def test_set_uri_local(fdb1_loc):
    run_coro_in_loop(a_test_set_uri_local, (fdb1_loc,))


async def a_test_set_uri_local(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a')

    # test of a insert, no transaction no party
    fob = None
    with pytest.raises(FdbException):
        fob = await fdb1_loc.new_ob_uri(None, t1uri )

    t_id = await fdb1_loc.begin_transaction()
    fob = await fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
        'key_int' : 391
        })

    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob().uri == fob_get().uri

