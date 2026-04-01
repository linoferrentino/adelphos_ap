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
from app.core.Adelphos import ad_errno
from app.core.MemoryAdelphosDao import MemoryAdelphosDao


# this is the local world
@pytest.fixture(scope = "module")
def w_local():

    ma_dao = MemoryAdelphosDao()
    adelphos1 = Adelphos('w1', ma_dao)
    return adelphos1


def test_add_alias(w_local):

    lino_id = w_local.alias_create('lino', 'ferre')
    assert lino_id > 0


def xtest_add_dup_family(w_local):

    lino_id = w_local.alias_create('lino', 'ferre')
    assert lino_id > 0
    bob_id = w_local.alias_create('bob', 'ferre')
    assert bob_id == -1
    assert ad_errno == EAdCore.EDUPLICATED_FAMILY


