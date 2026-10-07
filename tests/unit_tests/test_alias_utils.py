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
import app.misc.utils as misc

from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno

def test_alias_check():

    (alias, family) = misc.split_alias('lino.ferre', True)
    assert alias == 'lino'
    assert family == 'ferre'

    with pytest.raises(AdelphosCoreException) as fex:
        (alias, family) = misc.split_alias('lino.ferre.eo', True)

    assert fex.value.errno == ECoreErrno.EINVALID_ALIAS_SYNTAX

    with pytest.raises(AdelphosCoreException) as fex:
        (alias, family) = misc.split_alias('.linoferre', True)

    assert fex.value.errno == ECoreErrno.EINVALID_ALIAS_SYNTAX

    with pytest.raises(AdelphosCoreException) as fex:
        (alias, family) = misc.split_alias('linoferre.', True)

    assert fex.value.errno == ECoreErrno.EINVALID_ALIAS_SYNTAX

    with pytest.raises(AdelphosCoreException) as fex:
        (alias, family) = misc.split_alias('#lino.ferre', True)

    assert fex.value.errno == ECoreErrno.EINVALID_ALIAS_SYNTAX

    with pytest.raises(AdelphosCoreException) as fex:
        (alias, family) = misc.split_alias('lino.=ferre', True)

    assert fex.value.errno == ECoreErrno.EINVALID_ALIAS_SYNTAX

