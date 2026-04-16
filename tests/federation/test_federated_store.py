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
# we have to test the federation without adelphos
#from app.dao.AdelphosUri import AdelphosUri
#from app.dao.AdelphosUri import EAdelphosType
from app.federation.FederatedObject import FederatedObject
from app.federation.FederatedUri import FederatedUri

# we have the transport and a federated db

# as long as they are unique we are fine.
TYPE_T1 = "TYPE_T1"
TYPE_T2 = "TYPE_T2"


class FederatedUriTest(FederatedUri):

    def unparse(self):
        base_name = "XX" + self.ob_type + "/" + self.name
        if self.family is not None:
            base_name += f"_f{self.family}"
        if self.host is not None:
            base_name += f"_f{self.host}"
        if self.fragment is not None:
            base_name += f"_f{self.fragment}"
        return base_name


# we test with these two objects
class FedeObClass1(FederatedObject):
    pass


@pytest.fixture
def fdb1_loc():

    db = MemoryStore()
    #sr = SyncRouter()
    fdg = FederatedStore('www.h1.com', db, None)
    return fdg


def test_set_uri_local(fdb1_loc):

    #fob1 = FedeObClass1()

    t1uri = FederatedUriTest(TYPE_T1, 'a')

    # a local uri
    #uri = AdelphosUri(EAdelphosType.ALIAS_TYPE, None, 
    #                  name = 'lino', family = 'ferre' )

    # the alias 
    fob = fdb1_loc.create_uri(None, t1uri, 1)



