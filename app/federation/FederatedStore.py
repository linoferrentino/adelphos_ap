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
import threading
import yaml
import asyncio
from asyncio import TaskGroup

from app.misc.WrapInt import WrapInt
from app.transport.RouterProvider import RouterProvider
from enum import IntEnum
from enum import StrEnum
from enum import auto
from datetime import datetime
from app.sdc.Dependency import Dependency
from app.sdc.Dependencies import Dependencies
from app.federation.LifespanAware import LifespanAware
from app.federation.FederatedObject import FederatedObject
from app.federation.SocialListener import SocialListener
from app.federation.FederatedObject import str_to_fob
from app.federation.FederatedObject import REF_COUNT_COLUMN
from app.federation.FederatedObject import VERSION_COLUMN
from app.federation.FederatedObject import EObState
from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors
from app.federation.FederatedUri import FederatedUri
from app.federation.FederatedFactory import FederatedFactory

from app.transport.bridge.loop import run_coro_in_loop
from app.store.MemoryStore import MemoryStore
from app.store.SqliteStore import SqliteStore

from dataclasses import dataclass
from app.logging import gCon

from app.misc.WrapInt import W32

import traceback
import weakref


class FederatedTransaction:

    def __init__(self, tid, fdb):
        self.tid = tid
        self.fdb = fdb
        self.created_uris = {}
        self.locked_uris = {} 
        self.deleted_uris = {}
        self.read_uris = {} 
        self.begin_transaction = datetime.now()


    def _check_read_consistency(self):
        # XXX to do
        pass


    def _do_deletes(self):
        for k, v in self.deleted_uris.items():
            self._delete_uri_str(k)


    def _do_creates(self):
        for k,v in self.created_uris.items():
            gCon.log(f"check creates {v.ob}")
            if v.ob.fields[REF_COUNT_COLUMN] == 0:
                continue
            self._update_uri_str(k, v)
        self.created_uris.clear()


    def _do_updates(self):
        for k,v in self.locked_uris.items():
            gCon.log(f"check updates {k} = {v.ob}")
            if ((v.ob.state == EObState.PRESENT) and
                (v.ob.fields[REF_COUNT_COLUMN] == 0)):
                self._delete_uri_str(k)
                continue
            if v.modified == False:
                # XXX check read consistency
                gCon.log(f"{id(v)} NO MODIFIED")
                continue
            if v.ob.state == EObState.BORROWED:
                self.fdb.return_object(k, v)
            else:
                assert ((v.ob.state == EObState.PRESENT) or
                        (v.ob.state == EObState.LENT))
                self._update_uri_str(k, v)
        self.locked_uris.clear()


    def _delete_uri_str(self, key_str):
        self.fdb.db.del_key(key_str)


    def _update_uri_str(self, key_str, fob):
        if (fob.ob.state == EObState.PRESENT):
            fob.enforce_schema_before_commit()
            new_version = W32.inc_and_get_val(int(fob.ob.fields[VERSION_COLUMN]))
            fob.ob.fields[VERSION_COLUMN] = new_version
        ob_str = fob.to_store_str()
        gCon.log(f"Set {key_str} = {ob_str}")
        self.fdb.db.set(key_str, ob_str)


    def _release_all_locks(self):
        self.locked_uris.clear()


    def t_rollback(self):
        self._release_all_locks()
        

    def t_commit(self):

        try:

            self._check_read_consistency()

            self._do_deletes()

            self._do_updates()

            self._do_creates()

            self.fdb.db.commit()

            return

        except FdbException as fdbex:
            fdex = fdbex

        except Exception as ex:
            traceback.print_exc()
            fdex = FdbException(EFdbErrors.EFDB_INTERNAL_ERROR, str(ex)) 

        self.fdb.db.rollback()
        raise fdex

    def new_ob(self, fob):
        key_uri = fob.uri.unparse()

        #if self.locked_uris.get(key_uri) is not None:
        #    raise FdbException(EFdbErrors.EFDB_URI_EXISTS)

        #if self.deleted_uris.get(key_uri) is not None:
        #    raise FdbException(EFdbErrors.EFDB_URI_DELETED)
        
        #gCon.log(f"storing key {key_uri} in local db")
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

    uri_ob : FederatedUri
    t_id : uuid
    maybe: bool  = False
    uri_str: str = None
    must_lock: bool = False 
    tob : FederatedTransaction = None
    fob : FederatedObject = None

 
class FederatedStore(Dependency, LifespanAware):

    def __init__(self, kernel, *, db_type = None, schema = None):
        super().__init__(kernel)

        self.db_type = db_type
        self.db_name = ':memory:' 

        if isinstance(schema, str):
            schema_dict = yaml.safe_load(schema)
            self.schema = schema_dict
        else:
            self.schema = schema

        self.transactions = {}
        self.fact = FederatedFactory()
        self.hostname = kernel.conf().get_host()


    def _create_db(self, db_type, db_name):
        gCon.log(f"[yellow]Opening federated store {db_name} type {db_type}[/yellow]")
        if db_type == 'mem':
            db = MemoryStore()
        else:
            db = SqliteStore(db_name)
        return db


    async def _fdb_worker(self):
        self.fdbtg = TaskGroup()
        async with self.fdbtg:
            while self.run_enabled:
                async with self.stop_signal:
                    await self.stop_signal.wait()
            while self.background_tasks > 0:
                gCon.log(f"{self.background_tasks} tasks still running.")
                await asyncio.sleep(0.5)
            gCon.log(f"end of the _fdb_worker")


    async def start_async(self):

        config = self.conf.get_conf(Dependencies.FEDERATED_DB)

        self.run_enabled = True
        self.background_tasks = 0
        self.ses_worker = asyncio.create_task(self._fdb_worker())
        self.stop_signal = asyncio.Condition()

        if self.db_type is None:
            if config is None:
                self.db_type = 'mem'
                self.db_name = ':memory:'
            else:
                self.db_type = config.get('db_type', 'mem')
                self.db_name = config.get('db_name', ':memory:')

        if self.schema is None:
            raise Exception('loading of schema not yet supported')

        self.db = self._create_db(self.db_type, self.db_name)
        self.fact.parse_schema(self.schema)
        self.db.open()


    async def stop_async(self):
        gCon.log(f"receiving stop signal, waiting background async tasks")
        self.run_enabled = False
        async with self.stop_signal:
            self.stop_signal.notify_all()
        gCon.log("Waiting the session worker...")
        await self.ses_worker
        gCon.log("After wait session worker.")
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
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_TRANSACTION, t_id)
        return t_ob


    async def is_present_uri_str(self, t_id, uri):
        t_ob = self.get_tob_safe(t_id)
        return await self.is_present_uri(t_ob, uri)


    async def is_present_uri(self, t_ob, uri):
        key_uri = uri.unparse()

        exists_trx = t_ob.exists_ob(key_uri)

        if exists_trx is None:
            exists_trx = self.db.has_key(key_uri)

        return exists_trx


    async def ensure_uri_not_existing(self, t_ob, uri):

        exists_trx = await self.is_present_uri(t_ob, uri)

        if exists_trx == True:
            raise FdbException(EFdbErrors.EFDB_URI_EXISTS, uri)


    async def new_ob_uri(self, t_id, uri, fields = {} ):
        registrar = self.fact.get_registrar(uri.ob_type)
        if registrar is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_TYPE)

        uri_loc = self.remove_localhost(uri)
        return await self.new_ob_from_uri_coro(t_id, registrar, uri_loc, fields)


    async def new_ob(self, t_id, ob_type, name, *, fields = {} , **kwargs):

        registrar = self.fact.get_registrar(ob_type)
        if registrar is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_TYPE, ob_type)

        uri = self.fact.uri_constructor(ob_type, name, **kwargs)

        return await self.new_ob_from_uri_coro(t_id, registrar, uri, fields)


    def parse_uri(self, uri_str):
        parse_fn = getattr(self.fact.uri_constructor, 'parse')
        uri_ob = parse_fn(uri_str)
        return uri_ob


    def return_object(self, key, ob):
        self.background_tasks += 1
        self.fdbtg.create_task(FederatedStore.return_object_task(self, key, ob))


    async def return_object_task(self, key, ob):
        try:
            await self.return_object_task_try(key, ob)
        except Exception as ex:
            traceback.print_exc(ex)
            gCon.log("Got exception in return object!")
        finally:
            gCon.log("[red]end of remote request[/red]")
            self.background_tasks -= 1
            async with self.stop_signal:
                self.stop_signal.notify_all()


    async def return_object_task_try(self, key, ob):
        host = ob.uri.host
        gCon.log(f"I must return the object! key {key} ob {ob} host {host}")
        ob_str = ob.to_store_str()
        social_api = self.kernel.get_dep(Dependencies.SOCIAL_API)
        res = await social_api.remote_req('fdb', 'return', host, uri_str
                    = key, obstr = ob_str)

    async def new_ob_from_uri_coro(self, t_id, registrar, uri, fields):
        
        t_ob = self.get_tob_safe(t_id)

        await self.ensure_uri_not_existing(t_ob, uri)

        fob = FederatedObject(uri, registrar, fields = fields, locked = True)
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


    async def _read_remote_ctx(self, rctx):
        host = rctx.uri_ob.host
        social_api = self.kernel.get_dep(Dependencies.SOCIAL_API)
        res = await social_api.remote_req('fdb', 'borrow', host, uri_str =
                    rctx.uri_str, lock = rctx.must_lock)
        gCon.log(f"got {res} as response")
        remote_ob_str = res['obstr']
        return remote_ob_str


    async def _read_ctx(self, rctx):
        rctx.tob = self.get_tob_safe(rctx.t_id)
        rctx.uri_ob = self.remove_localhost(rctx.uri_ob)

        rctx.uri_str = rctx.uri_ob.unparse()
        rctx.fob = rctx.tob.get_ob(rctx.uri_str)
        if rctx.fob is not None:
            return

        t_ob_str = self.db.get_maybe(rctx.uri_str) 
        new_state = None
        if ((t_ob_str is None) and (rctx.uri_ob.host is not None)):
            t_ob_str = await self._read_remote_ctx(rctx)
            gCon.log(f"Got {t_ob_str} as the remote string")
            if rctx.must_lock:
                new_state = EObState.BORROWED
            else:
                new_state = EObState.CLONED

        if t_ob_str is None:
            if rctx.maybe:
                return None
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_OB, rctx.uri_str)

        ob_type = rctx.uri_ob.ob_type
        registrar = self.fact.get_registrar(ob_type)
        rctx.fob = str_to_fob(rctx.uri_ob, registrar, t_ob_str,
                              rctx.must_lock)
        if new_state is not None:
            rctx.fob.ob.state = new_state
        rctx.tob.read_ob_ctx(rctx)


    async def uri_read_lock(self, t_id, uri_ob, maybe = False):
        rctx = FedStore_ReadCtx(uri_ob, t_id, must_lock = True, maybe = maybe) 
        await self._read_ctx(rctx)
        return weakref.ref(rctx.fob)


    async def uri_read_str(self, t_id, uri_str, *, maybe = False,
                           must_lock = True):
        uri_ob = self.parse_uri(uri_str)
        rctx = FedStore_ReadCtx(uri_ob, t_id, must_lock = must_lock, 
                                maybe = maybe) 
        return await self._read_ref(rctx)


    async def _read_ref(self, rctx):
        await self._read_ctx(rctx)
        if rctx.fob is None:
            return None
        return weakref.ref(rctx.fob)


    async def uri_read_no_lock(self, t_id, uri_ob, maybe = False):

        rctx = FedStore_ReadCtx(uri_ob, t_id, must_lock = False, maybe = maybe) 
        await self._read_ctx(rctx)
        if rctx.fob is None:
            return None
        return weakref.ref(rctx.fob)


    async def begin_transaction(self):

        tid = uuid.uuid4()
        tob = FederatedTransaction(tid, self)
        self.transactions[tid] = tob
        return tid


    async def commit_transaction(self, t_id):
        t_ob = self.get_tob_safe(t_id)
        t_ob.t_commit()


    async def rollback_transaction(self, t_id):
        t_ob = self.get_tob_safe(t_id)
        t_ob.t_rollback()

