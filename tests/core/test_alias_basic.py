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

# this is the local world
@pytest.fixture(scope = "module")
def w_local():

    adelphos1 = Adelphos('w1', None)
    return adelphos1



def test_add_alias(w_local):
    assert 0 == 0
