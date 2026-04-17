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
from app.misc.WrapInt import WrapInt


def test_oob():

    with pytest.raises(Exception):
        wierr = WrapInt(1)
        
    with pytest.raises(Exception):
        wierr = WrapInt(32)
 
    with pytest.raises(Exception):
        wierr = WrapInt(3, 8)

    with pytest.raises(Exception):
        wierr = WrapInt(3, -1)


def test_w1():

    w1 = WrapInt(3, 4)

    val = w1.get_and_inc()
    assert(val == 4)

    val = w1.get_and_inc()
    assert(val == 5)


def test_wrap():

    w1 = WrapInt(3, 7)

    val = w1.get_and_inc()
    assert(val == 7)

    val = w1.get_and_inc()
    assert(val == 0)


def test_31():

    w1 = WrapInt()
    val = w1.get_and_inc()

    assert val >= 0
    assert val <= pow(2,31)
