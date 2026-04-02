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
from app.core.MemoryAdelphosDao import MemoryAdelphosDao
from app.core.SqliteAdelphosDao import SqliteAdelphosDao
from app.federation.MemoryAdelphosSocial import MemoryAdelphosSocial


# this is the local world
#@pytest.fixture(scope = "module")
@pytest.fixture
def w_local():

    ma_dao = MemoryAdelphosDao()
    #ma_dao = SqliteAdelphosDao(':memory:')
    social = MemoryAdelphosSocial()
    adelphos1 = Adelphos('w1', ma_dao, social)
    return adelphos1


def test_add_alias(w_local):

    lino_id = w_local.alias_create(0, 'lino', 'ferre', 'pass')
    assert lino_id > 0


def test_add_dup_family(w_local):

    lino_id = w_local.alias_create(0, 'lino', 'ferre', 'pass')
    assert lino_id > 0
    bob_id = w_local.alias_create(0, 'bob', 'ferre', 'pass')
    assert bob_id == -EAdErrno.EDUPLICATED_FAMILY


