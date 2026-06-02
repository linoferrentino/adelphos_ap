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
from app.logging import gCon

def test_query_info(app, aroutable):

    with app:

        url_query = f"/users/demo1"
        gCon.log("query {url_query}")
        response = app.get(url_query)
        assert response.status_code == 200 


