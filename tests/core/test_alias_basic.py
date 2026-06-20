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
from app.store.MemoryStore import MemoryStore
from app.core.algo.AdelphosAlgo import AdelphosAlgo 
from app.federation.FederatedStore import FederatedStore
from app.core.model.schema import adelphos_schema
from app.exc.AdelphosException import AdErrno


@pytest.fixture
def w_local():

    db = MemoryStore()
    fdb = FederatedStore('www.h1.com', db, adelphos_schema)
    model = AdelphosAlgo(fdb)
    return model 


def test_add_alias(w_local):

    lino_ob = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    assert lino_ob is not None


def Atest_add_dup_family(w_local):

    lino_ob = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    assert lino_ob is not None
    alice_ob = w_local.alias_algo.alias_create(0, 'alice', 'famal', 'pass99')
    assert alice_ob is not None
    bob_ob = w_local.alias_algo.alias_create(0, 'bob', 'ferre', 'pass')
    assert bob_ob == -AdErrno.EDUPLICATED_FAMILY


def OLDAP_test_login_pass(w_local):


    lino_id = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    res = w_local.alias_algo.login('lino', 'ferre', 'pass')
    assert res == lino_id

    res = w_local.alias_algo.login('lino', 'ferre', 'pass11')
    assert res == -AdErrno.EINVALID_USER_OR_PASSWORD
    res = w_local.alias_algo.login('lino', 'ferre1', 'pass')
    assert res == -AdErrno.EINVALID_USER_OR_PASSWORD
    res = w_local.alias_algo.login('lino1', 'ferre', 'pass')
    assert res == -AdErrno.EINVALID_USER_OR_PASSWORD


