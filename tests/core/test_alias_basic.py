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
from app.core.Adelphos import Adelphos
from app.core.EAdErrno import EAdErrno
#from app.core.MemoryAdelphosDao import MemoryAdelphosDao
from app.core.AdelphosDao import AdelphosDao
#from app.core.SqliteAdelphosDao import SqliteAdelphosDao
from app.store.MemoryStore import MemoryStore
from app.federation.MemoryAdelphosSocial import MemoryAdelphosSocial
from app.dao.AdelphosDb import AdelphosDb
from app.core.algo.AdelphosAlgo import AdelphosAlgo 

# this is the local world
#@pytest.fixture(scope = "module")
@pytest.fixture
def w_local():

    db = MemoryStore()
    model = AdelphosAlgo(0, db)
    return model 


# the alias is got from the URI

def test_add_alias(w_local):

    lino_id = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    assert lino_id > 0


def test_add_dup_family(w_local):

    lino_id = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    assert lino_id > 0
    alice_id = w_local.alias_algo.alias_create(0, 'alice', 'famal', 'pass99')
    assert alice_id > 0
    bob_id = w_local.alias_algo.alias_create(0, 'bob', 'ferre', 'pass')
    assert bob_id == -EAdErrno.EDUPLICATED_FAMILY


def test_login_pass(w_local):


    lino_id = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    res = w_local.alias_algo.login('lino', 'ferre', 'pass')
    assert res == lino_id

    res = w_local.alias_algo.login('lino', 'ferre', 'pass11')
    assert res == -EAdErrno.EINVALID_USER_OR_PASSWORD
    res = w_local.alias_algo.login('lino', 'ferre1', 'pass')
    assert res == -EAdErrno.EINVALID_USER_OR_PASSWORD
    res = w_local.alias_algo.login('lino1', 'ferre', 'pass')
    assert res == -EAdErrno.EINVALID_USER_OR_PASSWORD


