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

# a federated store is a distributed database in which objects
# are identified with an URI, AdelphosURI

# the store exposes a sync interface, but internally it might
# call async functions.



# the FederatedStore uses the transport to access objects which
# are beyond its reach and to perform a distributed commit.


# open uri 
# #al#lino.ferre@adelphos.it#objects.link
# the uri can have a fragment, this will lock only the corresponding part.

# Adelphos Database Daemon
DBSOCIAL_NAME = "AD_DB_D"


# the database can have the possibility to know the value of the link

# the store has a router it is needed to do remote queries.

import uuid

from app.misc.WrapInt import WrapInt
from app.transport.RouterProvider import RouterProvider
from enum import IntEnum
from enum import StrEnum
from enum import auto
from datetime import datetime
from app.federation.FederatedObject import FederatedObject
from app.federation.SocialListener import SocialListener
from app.federation.FederatedObject import str_to_fob
from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors
from app.federation.FederatedUri import FederatedUri
from dataclasses import dataclass

import traceback



# the federated store is not thread safe, but it is transaction safe,
# that is, it is able to memorize different transactions

# the object should be called by one thread, usually the async loop,
# the object will enter the loop already existing, if there is one.

# the store is not tied to a particular URI format: it could function with
# any type of uris, as long as they are unique and follow a common interface,
# the federated uri interface.


# the federated transaction collects all changed data in a coherent way.
# the transaction either it is commited or rolled back in full.
# the transaction is not durable, unless commited, during the building
# of the transaction the data is all in memory.
class FederatedTransaction:

    def __init__(self, tid, fdb):
        self.tid = tid
        self.fdb = fdb
        self.locked_uris = {} # they might be unmodified, but they belong to this tx
        self.deleted_uris = {}
        self.read_uris = {} # read only objects.
        self.begin_transaction = datetime.now()


    def _check_read_consistency(self):
        pass


    def _do_deletes(self):
        pass


    def _do_updates(self):
        for k,v in self.locked_uris.items():
            self._update_uri_str(k, v)


    def _update_uri_str(self, key_str, fob):
        self.fdb.db.set(key_str, fob.to_store_str())


    # important! the federated db is not thread safe, but internally it
    # has an async loop which can give a sort of paralellism
    def t_commit(self):

        # the commit in a federated transaction has become a local commit
        # in the local db, because all federated objects have been locked.
        try:

            self._check_read_consistency()

            self._do_deletes()

            self._do_updates()

            # If I am here I can commit the result
            self.fdb.db.commit()

        except FdbException as fdbex:
            self.fdb.db.rollback()

        except Exception as ex:
            traceback.print_exc()
            raise


    def new_ob(self, fob):
        key_uri = fob.uri.unparse()

        if self.locked_uris.get(key_uri) is not None:
            raise FdbException(EFdbErrors.EFDB_URI_EXISTS)

        if self.deleted_uris.get(key_uri) is not None:
            raise FdbException(EFdbErrors.EFDB_URI_DELETED)
        
        self.locked_uris[key_uri] = fob


    def get_ob_str(self, uri_str):

        if self.deleted_uris.get(uri_str) is not None:
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_OB)

        exist_val = self.locked_uris.get(uri_str)
        return exist_val


    def read_ob(self, key_uri, fob):
        self.read_uris[key_uri] = fob


class ELockResolution(StrEnum):

    FAIL_FAST = auto()
    RETRY_TIMEOUT = auto()


@dataclass
class FedStore_ReadCtx:
    """
    A simple structure used to store the reading context.
    
    This will take care also of the async context used to get the URI from the fediverse

    """
    uri_ob : FederatedUri
    t_id : uuid
    maybe: bool  = False
    uri_str: str = None
    must_lock: bool = False 
    only_local: bool = False
    lock_resolution : ELockResolution = ELockResolution.FAIL_FAST
    timeout_deadlock : int = 120
    tob : FederatedTransaction = None
    fob : FederatedObject = None

 
# the federated store uses a social network to synchronize to other peers.
class FederatedStore(SocialListener):


    # I initialize myself with my hostname to distinguish my own URIs from the others.
    def __init__(self, hostname, db, social):

        self.db = db
        self.hostname = hostname
        # you can use a federated store like a local store, in this case
        #if transport is not None:
        self.social = social
        if social is not None:
            social.register_listener(self)

        # at first the transaction set is empty
        self.transactions = {}


    async def new_post(self, post):
        pass


    # the store has its own async loop which is run forever.
    async def forever_db_main():
        pass


    def is_local_uri(self, uri):
        if uri.host is None:
            return True
        if uri.host == self.hostname:
            return True
        return False


    # the federated store can garbage collect the objects which are not
    # referenced anymore
    def gc(self):
        pass


    # this adds a federation host able to share values with myself.
    def add_federation_host(self, host):
        pass


    def remove_federation_host(self, host):
        pass


    #def get_uri_write(self, uri):
    #    pass


    # does a multiple compare and swap operation on the Federated store
    # as if has happened atomically or not.
    # every update is a tuple of two FederatedValue.
    def mcas(self, list_updates): 
        pass


    # locks the current URI, the URI is passed to the queried DB,
    # and it will update it with other URIs atomically.
    def grab_and_lock(self, uri):
        pass


    # this does not lock the object which remains property of the federated
    # store that holds it.
    def grab_no_lock(self, uri):
        pass


    # this function DOES NOT cross network boundaries.
    def _internal_mcas(self, ob_past, ob_new):
        pass


    # regains the updated URI which has been updated.
    def regain_updated_uri(self, uri):
        pass


    def get_tob_safe(self, t_id):
        if t_id is None:
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_TRANSACTION)
        t_ob = self.transactions.get(t_id)
        if t_ob is None:
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_TRANSACTION)
        return t_ob
 

    # creates an object with a certain URI and a certain reference count.
    # only some objects start with a reference count of one.
    def create_uri(self, t_id, uri_ob, ref_count = 0):

        # the uri must be local!
        if self.is_local_uri(uri_ob) == False:
            raise FdbException(EFdbErrors.EFDB_NO_LOCAL_URI)

        t_ob = self.get_tob_safe(t_id)

        if self.db.has_key(uri_ob.unparse()):
            raise FdbException(EFdbErrors.EFDB_URI_EXISTS)

        # a new object is by definition locked, because it starts in the
        # transaction
        fob = FederatedObject(uri_ob, ref_count, locked = True)
        t_ob.new_ob(fob)
        return fob


    def uri_snapshot(self, uri_ob):
        """ read a snapshot of an object, from this object you CANNOT modify the DB """
        pass




    def read_ob_in_transaction(self, t_ob, uri_ob, maybe = False):

        # 1. is it local? OK, take it, and put it into transaction.
        if self.is_local_uri(uri_ob) == False:
            if self.social is None:
                raise FdbException(EFdbErrors.EFDB_ONLY_LOCAL_STORE)
            return self.read_federated_uri(t_ob, uri_ob)

        # I can simply take the object locally.

        key_uri = uri_ob.unparse()

        t_ob_in_tx = t_ob.get_ob_str(key_uri)

        if t_ob_in_tx is not None:
            return t_ob_in_tx

        t_ob_str = self.db.get_maybe(key_uri) 

        if t_ob_str is None:
            if maybe:
                return None
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_OB)

        # pass the object read to the transaction.
        fob = str_to_fob(uri_ob, t_ob_str)
        t_ob.read_ob(key_uri, fob)

        return fob


    def _read_ctx(self, rctx):
        rctx.tob = self.get_tob_safe(rctx.t_id)
        rctx.uri_str = rctx.uri_ob.unparse()
        rctx.fob = rctx.tob.get_ob_str(rctx.uri_str)


    def uri_read_lock(self, t_id, uri_ob, lock_resolution = 'fail-fast'):
        """
        Reads an object and puts it into the working set of the current transaction.
    
        if the object is already locked use the lock_resolution method to know what to do
        """
        rctx = FedStore_ReadCtx(uri_ob, t_id, True) 
        self._read_ctx(rctx)
        return rctx.fob


    def uri_read_no_lock(self, t_id, uri_ob):

        t_ob = self.get_tob_safe(t_id)

        self.read_ob_in_transaction(t_ob, uri_ob)

        return fob


    # opens an URI not for update. It will not be part of the transaction, the result
    # is a FederatedValue
    def open_uri_maybe(self, uri_str):
        pass


    # opens the URI passing it as an object.
    def open_uri_ob_maybe(self, uri):
        pass


    # gets the object associated with this uri string.
    # if maybe is True it does not 
    # this is the generic method, clients may better use the other friendly methods.
    def open_fv_from_uri_str(self, uri_str, maybe = False, 
                     only_local = False, lock = False, create_if_not_exist = False):
        pass


    def get_uri_local_maybe(self, uri_str):
        pass


    ## this is a transaction: update a certain number of federated values.
    ## the idea is to commit all the locked objects.
    ## for now I do not see a use case where you should have a partial transaction.
    ## the commit might fail, if some transaction in the meantime has modified
    ## the same objects.
    #def commit(self, transaction_id):
    #    pass

    #
    #def rollback(self, transaction_id):
    #    pass


    #def set(self, key, value):
    #    self.db.set(key, value)


    #def update(self, ob):
    #    pass


    #def get_maybe(self, key):
    #    return self.db.get_maybe(key)


    # the store has the concept of a federated transaction, all transactions
    # live in isolation, the object returned must be passed to all the modifying
    # methods.
    def begin_transaction(self):

        tid = uuid.uuid4()
        tob = FederatedTransaction(tid, self)
        self.transactions[tid] = tob
        return tid


    #def get_and_lock_ob_uri(self, transaction_id, uri, maybe = False):
    #    pass


    ## this is used to create a new transaction.
    #def compare_and_swap_try(self, uri, old_val, new_val):
    #    pass


    #def compare_and_swap_commit(self, uri):
    #    pass


    # the idea of a federated store is that we have a certain number of URIs
    # to be updated.

    # I want them to be updated all or none, the transaction initiator will
    # get the resources and then it performs a CAS on all of them.

    # In case of failure it does a SAC (swap and compare) to return to the previous
    # item


    def commit_transaction(self, t_id):
        t_ob = self.get_tob_safe(t_id)
        t_ob.t_commit()


    #def rollback_transaction(self, transaction_id):
    #    pass

