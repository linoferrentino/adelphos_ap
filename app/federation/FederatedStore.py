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


import uuid
import copy
import sys

from app.misc.WrapInt import WrapInt
from app.transport.RouterProvider import RouterProvider
from enum import IntEnum
from enum import StrEnum
from enum import auto
from datetime import datetime
from app.sdc.Dependency import Dependency
from app.federation.LifespanAware import LifespanAware
from app.federation.FederatedObject import FederatedObject
from app.federation.SocialListener import SocialListener
from app.federation.FederatedObject import str_to_fob
from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors
from app.federation.FederatedUri import FederatedUri
from app.federation.FederatedFactory import FederatedFactory
from app.federation.Kernel import Kernel

from app.transport.bridge.loop import run_coro_in_loop
from app.store.MemoryStore import MemoryStore
from app.store.SqliteStore import SqliteStore

from dataclasses import dataclass
from app.logging import gCon

import traceback
import weakref


class ELockResolution(StrEnum):

    FAIL_FAST = auto()
    RETRY_TIMEOUT = auto()


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
        
        gCon.log(f"storing key {key_uri} in local db")
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

        #gCon.log(f"[red]{id(self)}[/red] asking {uri_str}")

        if self.deleted_uris.get(uri_str) is not None:
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_OB)

        exist_val = self.locked_uris.get(uri_str)
        if exist_val is not None:
            return exist_val

        #gCon.log(f"created uris {self.created_uris}")

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

 
class FederatedStore(Dependency, LifespanAware):


    def __init__(self, kernel, *, db_type = 'mem', schema = None):
        super().__init__(kernel)

        self.db = self._create_db(db_type)

        self.transactions = {}
        self.fact = FederatedFactory()

        self.hostname = kernel.conf().get_host()
        #gCon.log(f"Federated store host |{self.hostname}|")

        if (isinstance(schema, str)):
            raise Exception('loading of schema not yet supported')

        self.fact.parse_schema(schema)


    def _create_db(self, db_type):
        if db_type == 'mem':
            db = MemoryStore()
        else:
            db = SqliteStore()
        return db


    #def start(self):
    #    run_coro_in_loop(FederatedStore.start_async, (self,))
        

    async def start_async(self):
        self.db.open()


    async def stop_async(self):
        self.db.close()


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


    def is_present_object(self, t_ob, ob_type, name, **kwargs):
        uri = self.fact.uri_constructor(ob_type, name, **kwargs)
        return self.is_present_uri(t_ob, uri)
 

    def is_present_uri(self, t_ob, uri):
        key_uri = uri.unparse()

        exists_trx = t_ob.exists_ob(key_uri)

        if exists_trx is None:
            exists_trx = self.db.has_key(key_uri)

        return exists_trx


    def ensure_uri_not_existing(self, t_ob, uri):

        exists_trx = self.is_present_uri(t_ob, uri)

        if exists_trx == True:
            raise FdbException(EFdbErrors.EFDB_URI_EXISTS)


    def new_ob(self, t_id, ob_type, name, *, fields = {}, **kwargs):
        return run_coro_in_loop(self.new_ob_coro, 
                                (t_id, ob_type, name, fields, kwargs))


    def new_ob_uri(self, t_id, uri, fields = {} ):
        registrar = self.fact.get_registrar(uri.ob_type)
        if registrar is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_TYPE)

        uri_loc = self.remove_localhost(uri)
        return run_coro_in_loop(self.new_ob_from_uri_coro,
                                (t_id, registrar, uri_loc, fields))


    async def new_ob_coro(self, t_id, ob_type, name, fields , kwargs):

        registrar = self.fact.get_registrar(ob_type)
        if registrar is None:
            gCon.log(f"Unknown type {ob_type}")
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_TYPE, ob_type)

        #if registrar.needs_family == True:
        #    if family is None:
        #        raise FdbException(EFdbErrors.EFDB_REQUIRED_FAMILY_MISSING)

        #    #check_family = self.is_present_family()

        #else:
        #    if family is not None:
        #        raise FdbException(EFdbErrors.EFDB_FAMILY_NOT_WANTED)
        uri = self.fact.uri_constructor(ob_type, name, **kwargs)

        return await self.new_ob_from_uri_coro(t_id, registrar, uri, fields)
        

    async def new_ob_from_uri_coro(self, t_id, registrar, uri, fields):
        
        t_ob = self.get_tob_safe(t_id)

        self.ensure_uri_not_existing(t_ob, uri)

        fob = FederatedObject(uri, registrar, fields = fields, locked = True)
        #gCon.log(f"fob before {sys.getrefcount(fob)}")
        t_ob.new_ob(fob)
        #gCon.log(f"fob after {sys.getrefcount(fob)}")

        retref = weakref.ref(fob)
        #gCon.log(f"fob after weak {sys.getrefcount(fob)}")
        return retref


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


    async def _read_remote_ctx(self, rctx):
        #remote_ob_str = await self.fede_api.read_remote_uri(rctx)
        remote_ob_str = None
        return remote_ob_str


    async def _read_ctx(self, rctx):
        rctx.tob = self.get_tob_safe(rctx.t_id)
        rctx.uri_ob = self.remove_localhost(rctx.uri_ob)

        rctx.uri_str = rctx.uri_ob.unparse()
        rctx.fob = rctx.tob.get_ob(rctx.uri_str)
        if rctx.fob is not None:
            return

        #gCon.log(f"searching {rctx.uri_str}")

        first_pass = True
        while True:
            t_ob_str = self.db.get_maybe(rctx.uri_str) 
            #gCon.log(f"got the string {t_ob_str}")
            if (t_ob_str is None) and first_pass and (rctx.uri_ob.host is not None):
                first_pass = False
                t_ob_str = await self._read_remote_ctx(rctx)
                continue
            break

        if t_ob_str is not None:
            ob_type = rctx.uri_ob.ob_type
            registrar = self.fact.get_registrar(ob_type)
            rctx.fob = str_to_fob(rctx.uri_ob, registrar, t_ob_str, rctx.must_lock)
            rctx.tob.read_ob_ctx(rctx)
            return

        if rctx.maybe:
            return None
        raise FdbException(EFdbErrors.EFDB_NO_SUCH_OB, rctx.uri_str)


    def uri_read_lock(self, t_id, uri_ob):
        return run_coro_in_loop(self.uri_read_lock_coro, (t_id, uri_ob))


    async def uri_read_lock_coro(self, t_id, uri_ob):
        rctx = FedStore_ReadCtx(uri_ob, t_id, must_lock = True) 
        await self._read_ctx(rctx)
        return weakref.ref(rctx.fob)


    async def uri_read_no_lock_coro():
        pass


    def uri_read_no_lock(self, t_id, uri_ob, maybe = False):

        return run_coro_in_loop(self.uri_read_no_lock_coro, (t_id, uri_ob, maybe))


    async def uri_read_no_lock_coro(self, t_id, uri_ob, maybe = False):

        rctx = FedStore_ReadCtx(uri_ob, t_id, must_lock = False, maybe = maybe) 
        await self._read_ctx(rctx)
        if rctx.fob is None:
            return None
        return weakref.ref(rctx.fob)


    # the store has the concept of a federated transaction, all transactions
    # live in isolation, the object returned must be passed to all the modifying
    # methods.
    def begin_transaction(self):
        return run_coro_in_loop(self.begin_transaction_coro, ())


    async def begin_transaction_coro(self):

        tid = uuid.uuid4()
        tob = FederatedTransaction(tid, self)
        self.transactions[tid] = tob
        return tid


    def commit_transaction(self, t_id):
        run_coro_in_loop(self.commit_transaction_coro, (t_id,))


    async def commit_transaction_coro(self, t_id):
        t_ob = self.get_tob_safe(t_id)
        t_ob.t_commit()


    def rollback_transaction(self, t_id):
        run_coro_in_loop(self.rollback_transaction_coro, (t_id,))


    async def rollback_transaction_coro(self, t_id):
        t_ob = self.get_tob_safe(t_id)
        t_ob.t_rollback()

