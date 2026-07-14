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

from app.core.model.AdelphosUri import AdelphosUri
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from app.logging import gCon


def test_uri():


    with pytest.raises(AdelphosException) as fex:
        uri1 = AdelphosUri.parse("test.lino@host")
    assert fex.value.errno == AdErrno.EINVALID_URI

    uri1 = AdelphosUri.parse("#al#lino.ferre@host:99")
    assert uri1.family == 'ferre'
    assert uri1.name == 'lino'
    assert uri1.ob_type == 'al'
    assert uri1.host == 'host:99'

