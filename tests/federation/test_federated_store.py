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
import asyncio 

from app.federation.FederatedStore import FederatedStore
from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors
from app.store.MemoryStore import MemoryStore
from app.store.SqliteStore import SqliteStore
from app.logging import gCon


from tests.federation.schema_simple import LOCALHOST, LOCALHOST1
from tests.federation.schema_simple import FIRST_HOST, OTHERHOST
from tests.federation.schema_simple import TYPE_T1, TYPE_T2
from tests.federation.schema_simple import FederatedUriTest
from app.sdc.Dependencies import Dependencies
from tests.federation.fixtures import fdb1_loc
from tests.federation.fixtures import fdb_host
from tests.federation.fixtures import federated_db_local
from tests.federation.fixtures import federated_db
from app.transport.bridge.loop import run_coro_in_loop
from tests.federation.schema_simple import schema_simple_yaml
from tests.federation.schema_simple import schema_reserved_error
import tests.adelphoi_test_config as tconf


def test_new_object_f(fdb1_loc):

    run_coro_in_loop(a_test_new_object_f, (fdb1_loc,))


async def a_test_new_object_f(fdb1_loc):

    t_id = fdb1_loc.begin_transaction()

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

    fdb1_loc.commit_transaction(t_id)

    assert fob1() is None

    t1uri = FederatedUriTest(TYPE_T1, 'ob1', host = LOCALHOST)
    t1uri_1 = FederatedUriTest(TYPE_T1, 'ob1', host = LOCALHOST1)
    t_id = fdb1_loc.begin_transaction()
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

    t_id = fdb1_loc.begin_transaction()
    fob = await fdb1_loc.new_ob(t_id, TYPE_T1, 'a', fields = {
        'key_int' : 11
        })
    fob().set_scalar('key1', 'val1')
    fdb1_loc.commit_transaction(t_id)


async def a_fdb1_link_a(fdb1_loc):

    await a_fdb1_loc_a(fdb1_loc)

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t2uri = FederatedUriTest(TYPE_T2, 'a')
    t_id = fdb1_loc.begin_transaction()

    fob2 = await fdb1_loc.new_ob(t_id, TYPE_T2, 'a')

    fob1 = await fdb1_loc.uri_read_lock(t_id, t1uri)
    fob1().compare_and_swap_link('uses', None, fob2)

    fdb1_loc.commit_transaction(t_id)
 

def test_link2(fdb1_loc):

    run_coro_in_loop(a_test_link2, (fdb1_loc,))


async def a_test_link2(fdb1_loc):

    await a_fdb1_link_a(fdb1_loc)

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t2uri_old = FederatedUriTest(TYPE_T2, 'a')
    t2uri_new = FederatedUriTest(TYPE_T2, 'b')

    t_id = fdb1_loc.begin_transaction()

    fob1 = await fdb1_loc.uri_read_lock(t_id, t1uri)
    fob2_old = await fdb1_loc.uri_read_lock(t_id, t2uri_old)
    fob2_new = await fdb1_loc.new_ob_uri(t_id, t2uri_new)
    fob1().compare_and_swap_link('uses', fob2_old, fob2_new)

    fdb1_loc.commit_transaction(t_id)

    t_id = fdb1_loc.begin_transaction()

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

    t_id = fdb1_loc.begin_transaction()

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
    t_id = fdb1_loc.begin_transaction()

    fob2 = await fdb1_loc.new_ob_uri(t_id, t2uri)
    fob2_b = await fdb1_loc.new_ob_uri(t_id, t2urib)
    fob1 = await fdb1_loc.uri_read_lock(t_id, t1uri)
    fob1().compare_and_swap_link('uses', None, fob2)
    fdb1_loc.commit_transaction(t_id)

    t_id = fdb1_loc.begin_transaction()

    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t2uri)
    assert fob_get() != None
     
    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t2urib, True)
    assert fob_get == None


def test_write_over_rollback(fdb1_loc):
    run_coro_in_loop(a_test_write_over_rollback, (fdb1_loc,))


async def a_test_write_over_rollback(fdb1_loc):

    await a_fdb1_loc_a(fdb1_loc)

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t_id = fdb1_loc.begin_transaction()
    fob_get = await fdb1_loc.uri_read_lock(t_id, t1uri)
    val = fob_get().get_scalar('key1')
    assert val == 'val1'
    fob_get().set_scalar('key1', 'val1_new')
    val = fob_get().get_scalar('key1')
    assert val == 'val1_new'
    fdb1_loc.rollback_transaction(t_id)

    # this should not be possible
    with pytest.raises(AttributeError):
        fob_get().get_scalar('key1')

    t_id = fdb1_loc.begin_transaction()
    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    val = fob_get().get_scalar('key1')
    assert val == 'val1'
    

def test_after_transaction(fdb1_loc):

    run_coro_in_loop(a_test_after_transaction, (fdb1_loc,))


async def a_test_after_transaction(fdb1_loc):

    await a_fdb1_loc_a(fdb1_loc)

    t1uri = FederatedUriTest(TYPE_T1, 'a')
    t_id = fdb1_loc.begin_transaction()
    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    val = fob_get().get_scalar('key1')
    assert val == 'val1'
    assert t1uri == fob_get().uri


def test_set_uri_local_1(fdb1_loc):

    run_coro_in_loop(a_test_set_uri_local_1, (fdb1_loc,))


async def a_test_set_uri_local_1(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a', host = LOCALHOST)
    t_id = fdb1_loc.begin_transaction()
    fob = await fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
        'key_int' : 1032
        })
    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob().uri == fob_get().uri


def test_set_uri_no_loc(fdb1_loc):
    run_coro_in_loop(a_test_set_uri_no_loc, (fdb1_loc, ))


async def a_test_set_uri_no_loc(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a', host = 'www.h2.com')
    t_id = fdb1_loc.begin_transaction()
    with pytest.raises(FdbException):
        fob = await fdb1_loc.new_ob_uri(t_id, t1uri)


def test_create_alias(fdb1_loc):
    run_coro_in_loop(a_test_create_alias, (fdb1_loc,))


async def a_test_create_alias(fdb1_loc):
    t1uri = FederatedUriTest('al', 'a')
    t_id = fdb1_loc.begin_transaction()

    with pytest.raises(FdbException) as fex:
        fob = await fdb1_loc.new_ob_uri(t_id, t1uri)

    assert fex.value.errno == EFdbErrors.EFDB_REQUIRED_FIELD_MISSING

    fob = await fdb1_loc.new_ob_uri(t_id, t1uri, fields = { 'equity' : 99.2 })

    assert fob().get_scalar('equity') == 99.2


def test_uri_set(fdb1_loc):
    run_coro_in_loop(a_test_uri_set, (fdb1_loc,))


async def a_test_uri_set(fdb1_loc):
    t1uri = FederatedUriTest('t_uri_set', 'tj1')
    t_id = fdb1_loc.begin_transaction()
    fob = await fdb1_loc.new_ob_uri(t_id, t1uri)

    with pytest.raises(FdbException) as fex:
        fdb1_loc.commit_transaction(t_id)

    assert fex.value.errno == EFdbErrors.EFDB_REQUIRED_FIELD_MISSING

    tmember_uri = FederatedUriTest('t_member', 'member_lino', host = LOCALHOST)
    fob_dep = await fdb1_loc.new_ob_uri(t_id, tmember_uri, fields = {
        'name' : 'lino'
        })
    
    with pytest.raises(FdbException) as fex:
        fob().set_link('members', fob_dep)
    assert fex.value.errno == EFdbErrors.EFDB_SCALAR_UNEXPECTED

    with pytest.raises(FdbException) as fex:
        fdb1_loc.commit_transaction(t_id)
    assert fex.value.errno == EFdbErrors.EFDB_REQUIRED_FIELD_MISSING
    assert re.search('members$', fex.value.out_str)

    fob().add_link('members', fob_dep)

    fdb1_loc.commit_transaction(t_id)

    t_id = fdb1_loc.begin_transaction()

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
        fdb1_loc.commit_transaction(t_id)
    assert fex.value.errno == EFdbErrors.EFDB_CARDINALITY_LOWER


def test_enum_field(fdb1_loc):
    run_coro_in_loop(a_test_enum_field, (fdb1_loc,))


async def a_test_enum_field(fdb1_loc):
    t1uri = FederatedUriTest('p_enum', 'e1')
    t_id = fdb1_loc.begin_transaction()

    with pytest.raises(FdbException) as fex:
        fob = await fdb1_loc.new_ob_uri(t_id, t1uri)
    assert fex.value.errno == EFdbErrors.EFDB_REQUIRED_FIELD_MISSING

    with pytest.raises(FdbException) as fex:
        fob = await fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
            'name' : 'John',
            'preferred_fruit' : 'strawberry',
        })
    assert fex.value.errno == EFdbErrors.EFDB_INVALID_ENUM_VALUE

    fob = await fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
            'name' : 'John',
            'preferred_fruit' : 'apple',
        })

    pref_fruit = fob().get_scalar('preferred_fruit')
    assert pref_fruit == 'apple'

    pref_fruit = fob().get_scalar('second_preferred_fruit')
    assert pref_fruit == 'banana'

    fdb1_loc.commit_transaction(t_id)

    t_id = fdb1_loc.begin_transaction()
    fob = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob() is not None

    pref_fruit = fob().get_scalar('preferred_fruit')
    assert pref_fruit == 'apple'

    pref_fruit = fob().get_scalar('second_preferred_fruit')
    assert pref_fruit == 'banana'




    
def test_json_field(fdb1_loc):
    run_coro_in_loop(a_test_json_field, (fdb1_loc,))


async def a_test_json_field(fdb1_loc):

    t1uri = FederatedUriTest('t_json', 'tj1')
    t_id = fdb1_loc.begin_transaction()
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

    fdb1_loc.commit_transaction(t_id)
    t_id = fdb1_loc.begin_transaction()
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


def test_impossibile_column(federated_db):
    wrap1 = federated_db(FIRST_HOST, tconf.federated_store_kernel_template,
                         schema_reserved_error)

    with pytest.raises(FdbException) as fex:
        with wrap1:
            pass
    assert fex.value.errno == EFdbErrors.EFDB_RESERVED


def test_remote_uri(federated_db):
    wrap1 = federated_db(FIRST_HOST, tconf.federated_store_network_template,
                         schema_simple_yaml)
    wrap2 = federated_db(OTHERHOST, tconf.federated_store_network_template,
                         schema_simple_yaml)

    with wrap1, wrap2:
        fdb1 = wrap1.app.routable.get_dep(Dependencies.FEDERATED_DB)
        fdb2 = wrap2.app.routable.get_dep(Dependencies.FEDERATED_DB)
        run_coro_in_loop(a_test_remote_uri, (fdb1, fdb2))


async def _create_object_uri_in_transaction(fdb, uri, fields = {}):
    tid = fdb.begin_transaction()
    await fdb.new_ob_uri(tid, uri, fields)
    fdb.commit_transaction(tid)


async def _create_object_in_isolated_tx(fdb, uri_type, uri_name, host = None,
                                        fields = {}):
    ob_uri = FederatedUriTest(uri_type, uri_name, host = host)
    await _create_object_uri_in_transaction(fdb, ob_uri, fields)


async def a_test_remote_uri(fdb1, fdb2):
    t1uri = FederatedUriTest('al_uri', 'a1', host = FIRST_HOST)
    t2uri = FederatedUriTest('al_uri', 'a2', host = OTHERHOST)

    await _create_object_uri_in_transaction(fdb1, t1uri)
    await _create_object_uri_in_transaction(fdb2, t2uri)

    tid1 = fdb1.begin_transaction()

    flocal = await fdb1.uri_read_lock(tid1, t1uri)
    fremote = await fdb1.uri_read_lock(tid1, t2uri)
    assert fremote is not None

    tline_ob = await fdb1.new_ob(tid1, 'tline', 'tt1', fields = {
        'equity' : 99.9,
        })
    assert tline_ob is not None
    gCon.log(f"Created the ob {tline_ob().uri}")

    with pytest.raises(FdbException) as fex:
        flocal().add_link('tlines', tline_ob)
    assert fex.value.errno == EFdbErrors.EFDB_UNKNOWN_COLUMN

    fremote().add_link('trust_lines', tline_ob)
    flocal().add_link('trust_lines', tline_ob)

    fdb1.commit_transaction(tid1)

    tid2 = fdb2.begin_transaction()
    with pytest.raises(FdbException) as fex:
        local = await fdb2.uri_read_lock(tid2, t2uri)
    assert fex.value.errno == EFdbErrors.EFDB_LENT

    gCon.log(f"Waiting")
    await asyncio.sleep(.5)

    local = await fdb2.uri_read_lock(tid2, t2uri)
    gCon.log(f"the {local().uri} (remote) object is present!")

    #assert local is not None

    #trust_lines = local().get_as_list('trust_lines')
    #gCon.log(f"trust lines are {trust_lines}")
    #assert len(trust_lines) == 1



def test_set_uri_local(fdb1_loc):
    run_coro_in_loop(a_test_set_uri_local, (fdb1_loc,))


async def a_test_set_uri_local(fdb1_loc):

    t1uri = FederatedUriTest(TYPE_T1, 'a')

    # test of a insert, no transaction no party
    fob = None
    with pytest.raises(FdbException):
        fob = await fdb1_loc.new_ob_uri(None, t1uri )

    t_id = fdb1_loc.begin_transaction()
    fob = await fdb1_loc.new_ob_uri(t_id, t1uri, fields = {
        'key_int' : 391
        })

    fob_get = await fdb1_loc.uri_read_no_lock(t_id, t1uri)
    assert fob().uri == fob_get().uri

