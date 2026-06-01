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

from tests.testers.fixtures import app, aroutable
import tests.adelphoi_test_config as tconf

import app.consts as CNST

def test_query_info(app, aroutable):

    url_query = f"{CNST.WEBFINGER_ROUTE}?val=wrong"
    response = app.get(url_query)
    assert response.status_code == 401


