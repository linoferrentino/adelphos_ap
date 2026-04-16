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
from app.federation.FederatedStore import FederatedStore
from app.transport.SyncRouter import SyncRouter
from app.store.MemoryStore import MemoryStore
from app.dao.AdelphosUri import AdelphosUri
from app.dao.AdelphosUri import EAdelphosType

# we have the transport and a federated db

@pytest.fixture
def federated_1_local():

    db = MemoryStore()
    #sr = SyncRouter()
    fdg = FederatedStore('www.h1.com', db, None)
    return db 


def test_set_uri_local(federated_1_local):

    uri = AdelphosUri()

