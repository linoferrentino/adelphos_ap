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
import json
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend


def test_query_info(app, aroutable):

    with app:
        url_query = f"/api/users/t1"
        response = app.get(url_query)
        assert response.status_code == 200 
        if hasattr(response, 'body'):
            content = response.body
        else:
            content = response.content
        content_str = content.decode()
        cont_ob = json.loads(content_str)
        assert cont_ob['publicKey']['publicKeyPem'] is not None
        public_key = cont_ob['publicKey']['publicKeyPem']

        remote_public_key = crypto_serialization.load_pem_public_key(
                public_key.encode(), backend=crypto_default_backend())



def test_query_info_ko(app, aroutable):

    url_query = f"/users/demo99"
    response = app.get(url_query)
    assert response.status_code == 404



