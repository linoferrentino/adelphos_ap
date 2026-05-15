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


# the database can have the possibility to know the value of the link

# the store has a router it is needed to do remote queries.

import uuid
import copy

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
from app.federation.FederatedFactory import FederatedFactory
from app.federation.SocialGateway import SocialGateway
from app.federation.FederatedStoreApi import FederatedStoreApi

from app.transport.bridge.loop import run_coro_in_loop

from dataclasses import dataclass
from app.logging import gCon

import traceback
import weakref


class ELockResolution(StrEnum):

    FAIL_FAST = auto()
    RETRY_TIMEOUT = auto()



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
        self.created_uris = {}
        self.locked_uris = {} # they might be unmodified, but they belong to this tx
        self.deleted_uris = {}
        self.read_uris = {} # read only objects.
        self.begin_transaction = datetime.now()


    def _check_read_consistency(self):
        # XXX to do
        pass


    def _do_deletes(self):
        for k, v in self.deleted_uris.items():
            self._delete_uri_str(k)


    def _do_creates(self):
        for k,v in self.created_uris.items():
            if v.ob.ref_count == 0:
                continue
            self._update_uri_str(k, v)
        self.created_uris.clear()


    def _do_updates(self):
        for k,v in self.locked_uris.items():
            if v.ob.ref_count == 0:
                self._delete_uri_str(k)
                continue
            if v.modified == False:
                # XXX check read consistency
                continue
            self._update_uri_str(k, v)
        self.locked_uris.clear()


    def _delete_uri_str(self, key_str):
        self.fdb.db.del_key(key_str)


    def _update_uri_str(self, key_str, fob):
        self.fdb.db.set(key_str, fob.to_store_str())


    def _release_all_locks(self):
        self.locked_uris.clear()


    def t_rollback(self):
        """ the rollback will release all the locks """
        self._release_all_locks()
        

    # important! the federated db is not thread safe, but internally it
    # has an async loop which can give a sort of paralellism
    def t_commit(self):

        # the commit in a federated transaction has become a local commit
        # in the local db, because all federated objects have been locked.
        try:

            self._check_read_consistency()

            self._do_deletes()

            self._do_updates()

            self._do_creates()

            # If I am here I can commit the result
            self.fdb.db.commit()

        except FdbException as fdbex:
            self.fdb.db.rollback()

        except Exception as ex:
            traceback.print_exc()
            raise


    def new_ob(self, fob):
        key_uri = fob.uri.unparse()

        #if self.locked_uris.get(key_uri) is not None:
        #    raise FdbException(EFdbErrors.EFDB_URI_EXISTS)

        #if self.deleted_uris.get(key_uri) is not None:
        #    raise FdbException(EFdbErrors.EFDB_URI_DELETED)
        
        self.created_uris[key_uri] = fob


    def exists_ob(self, key_uri):

        if self.deleted_uris.get(key_uri) is not None:
            return False

        if self.read_uris.get(key_uri) is not None:
            return True

        if self.locked_uris.get(key_uri) is not None:
            return True

        if self.created_uris.get(key_uri) is not None:
            return True

        return None


    def get_ob(self, uri_str):

        if self.deleted_uris.get(uri_str) is not None:
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_OB)

        exist_val = self.locked_uris.get(uri_str)
        if exist_val is not None:
            return exist_val

        maybe_created = self.created_uris.get(uri_str)
        if maybe_created is not None:
            return maybe_created

        return None


    def read_ob(self, key_uri, fob):
        self.read_uris[key_uri] = fob


    def read_ob_ctx(self, rctx):
        if rctx.must_lock:
            self.locked_uris[rctx.uri_str] = rctx.fob
        else:
            self.read_uris[rctx.uri_str] = rctx.fob


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
class FederatedStore:


    # I initialize myself with my hostname to distinguish my own URIs from the others.
    def __init__(self, hostname, db, social, schema_init):

        self.db = db
        self.hostname = hostname

        self.fede_api = FederatedStoreApi(social)

        # at first the transaction set is empty
        self.transactions = {}

        schema_init()


    #async def new_post(self, post):
    #    pass


    ## the store has its own async loop which is run forever.
    #async def forever_db_main():
    #    pass


    def is_local_uri(self, uri):
        if uri.host is None:
            return True
        if uri.host == self.hostname:
            return True
        return False


    def get_tob_safe(self, t_id):
        if t_id is None:
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_TRANSACTION)
        t_ob = self.transactions.get(t_id)
        if t_ob is None:
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_TRANSACTION)
        return t_ob
 

    # creates an object with a certain URI and a certain reference count.
    # only some objects start with a reference count of one.
    # deprecated, use new_ob instead
    def create_uri(self, t_id, uri_ob, ref_count = 0):

        # the uri must be local!
        if self.is_local_uri(uri_ob) == False:
            raise FdbException(EFdbErrors.EFDB_NO_LOCAL_URI)

        uri_ob = self.remove_localhost(uri_ob)

        t_ob = self.get_tob_safe(t_id)

        self.ensure_uri_not_existing(t_ob, uri_ob)

        # a new object is by definition locked, because it starts in the
        # transaction
        fob = FederatedObject(uri_ob, ref_count, locked = True)
        t_ob.new_ob(fob)
        return weakref.ref(fob)


    def _is_present_uri(self, t_ob, uri):
        key_uri = uri.unparse()

        exists_trx = t_ob.exists_ob(key_uri)

        if exists_trx is None:
            exists_trx = self.db.has_key(key_uri)

        return exists_trx


    def ensure_uri_not_existing(self, t_ob, uri):

        exists_trx = self._is_present_uri(t_ob, uri)

        if exists_trx == True:
            raise FdbException(EFdbErrors.EFDB_URI_EXISTS)


    def new_ob(self, t_id, ob_type, name, family = None, fields = {}):

        registrar = FederatedFactory.get_registrar(ob_type)
        if registrar is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_TYPE)

        if registrar.needs_family == True:
            if family is None:
                raise FdbException(EFdbErrors.EFDB_REQUIRED_FAMILY_MISSING)
        else:
            if family is not None:
                raise FdbException(EFdbErrors.EFDB_FAMILY_NOT_WANTED)

        uri = FederatedFactory.uri_constructor(ob_type, name, family)
        
        t_ob = self.get_tob_safe(t_id)

        self.ensure_uri_not_existing(t_ob, uri)

        if registrar.first_class:
            ref_count = 1
        else:
            ref_count = 0

        fob = registrar.constructor(uri, ref_count, fields = fields, locked = True)
        t_ob.new_ob(fob)
        return weakref.ref(fob)


    def uri_snapshot(self, uri_ob):
        """ read a snapshot of an object, from this object you CANNOT modify the DB """
        pass


    def remove_localhost(self, uriob):
        if uriob.host is None:
            return uriob
        if ((uriob.host == self.hostname) or
            (uriob.host == '::1') or
            (uriob.host == 'localhost') or
            (uriob.host == '127.0.0.1')):
            copied_uri = copy.copy(uriob)
            copied_uri.host = None
            return copied_uri
        return uriob


    def _read_remote_ctx(self, rctx):
        remote_ob_str = self.fede_api.read_remote_uri(rctx)
        return remote_ob_str


    def _read_ctx(self, rctx):
        rctx.tob = self.get_tob_safe(rctx.t_id)
        rctx.uri_ob = self.remove_localhost(rctx.uri_ob)

        rctx.uri_str = rctx.uri_ob.unparse()
        rctx.fob = rctx.tob.get_ob(rctx.uri_str)
        if rctx.fob is not None:
            return

        first_pass = True
        while True:
            t_ob_str = self.db.get_maybe(rctx.uri_str) 
            if (t_ob_str is None) and first_pass and (rctx.uri_ob.host is not None):
                first_pass = False
                t_ob_str = self._read_remote_ctx(rctx)
                continue
            break

        if t_ob_str is not None:
            rctx.fob = str_to_fob(rctx.uri_ob, t_ob_str, rctx.must_lock)
            rctx.tob.read_ob_ctx(rctx)
            return

        if rctx.maybe:
            return None
        raise FdbException(EFdbErrors.EFDB_NO_SUCH_OB, rctx.uri_str)


    def uri_read_lock(self, t_id, uri_ob):
        """
        Reads an object and puts it into the working set of the current transaction.
    
        if the object is already locked use the lock_resolution method to know what to do
        """
        rctx = FedStore_ReadCtx(uri_ob, t_id, must_lock = True) 
        self._read_ctx(rctx)
        return weakref.ref(rctx.fob)


    async def uri_read_no_lock_coro():
        pass


    def uri_read_no_lock(self, t_id, uri_ob, maybe = False):

        rctx = FedStore_ReadCtx(uri_ob, t_id, must_lock = False, maybe = maybe) 
        self._read_ctx(rctx)
        if rctx.fob is None:
            return None
        return weakref.ref(rctx.fob)


    # the store has the concept of a federated transaction, all transactions
    # live in isolation, the object returned must be passed to all the modifying
    # methods.
    def begin_transaction(self):

        tid = uuid.uuid4()
        tob = FederatedTransaction(tid, self)
        self.transactions[tid] = tob
        return tid


    def commit_transaction(self, t_id):
        t_ob = self.get_tob_safe(t_id)
        t_ob.t_commit()


    def rollback_transaction(self, t_id):
        t_ob = self.get_tob_safe(t_id)
        t_ob.t_rollback()

