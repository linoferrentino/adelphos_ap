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
from app.federation.FederatedObject import str_to_fobs
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
        for k,v in self.read_uris.items():
            present_str = self.fdb.db.get_maybe(k)
            if v.ob.state == EObState.CLONED:
                if present_str is not None:
                    raise FdbException(EFdbErrors.EFDB_CONFLICT_DURING_COMMIT,
                                       f"{k} cloned but present, why?")
                return
            if present_str is None:
                raise FdbException(EFdbErrors.EFDB_OBJECT_GONE, k)
            obs = str_to_fobs(present_str)
            if obs.get_state == EObState.LENT:
                raise FdbException(EFdbErrors.EFDB_OBJECT_GONE, k)
            if obs.version != v.version:
                raise FdbException(EFdbErrors.EFDB_READ_INCOHERENT, k)


    def _do_deletes(self):
        for k, v in self.deleted_uris.items():
            self._delete_ob(k, v)


    def _do_creates(self):
        for k,v in self.created_uris.items():
            if v.ob.fields[REF_COUNT_COLUMN] == 0:
                gCon.log(f"will prepare {k} to oblivion")
                v.prepare_to_oblivion(self)
                continue
            present_str = self.fdb.db.get_maybe(k)
            if present_str is not None:
                raise FdbException(EFdbErrors.EFDB_CONFLICT_DURING_COMMIT,
                                   k)
            self._update_uri_str(k, v, True)


    def _return_all_borrows(self):
        for k,v in self.locked_uris.items():
            if v.ob.state == EObState.BORROWED:
                self.fdb.return_object(k)


    def _do_updates(self):
        for k,v in self.locked_uris.items():
            #gCon.log(f"{k} -> {v} check update")
            if ((v.ob.state == EObState.PRESENT) and
                (v.ob.fields[REF_COUNT_COLUMN] == 0)):
                self._delete_ob(k, v)
                continue
            if v.modified == False and v.ob.state != EObState.BORROWED:
                #gCon.log("not modified")
                continue
            self._update_uri_str(k, v)
            if self.do_mod_db == False:
                return
            if v.ob.state == EObState.BORROWED:
                if v.modified:
                    self.fdb.return_object(k, v)
                else:
                    self.fdb.return_object(k)
            else:
                assert ((v.ob.state == EObState.PRESENT) or
                        (v.ob.state == EObState.LENT) or
                        (v.ob.state == EObState.DETACHED))


    def _delete_ob(self, key_str, ob):
        ob.prepare_to_oblivion(self)
        if self.do_mod_db == False:
            return
        self.fdb.db.del_key(key_str)


    def _update_uri_str(self, key_str, fob, is_create = False):
        if self.do_mod_db == False:
            return
        present_ob_str = self.fdb.db.get_maybe(key_str)

        if fob.ob.state != EObState.LENT:
            fob.enforce_schema_before_commit()

        if fob.ob.state == EObState.BORROWED:
            if present_ob_str is not None:
                gCon.log(f"I have found {present_ob_str} as string for a borrowed object")
                raise FdbException(EFdbErrors.EFDB_CONFLICT_DURING_COMMIT,
                  f"{self.fdb.hostname} object {key_str} borrowed, cannot exist")

        elif (fob.ob.state != EObState.LENT):
            if is_create:
                if present_ob_str is not None:
                    raise FdbException(EFdbErrors.EFDB_CONFLICT_DURING_COMMIT,
                                   f"object {key_str} created")
            else:

                if present_ob_str is None:
                    raise FdbException(EFdbErrors.EFDB_CONFLICT_DURING_COMMIT,
                                   f"object {key_str} deleted")
                obs = str_to_fobs(present_ob_str)

                if obs.state == EObState.LENT:
                    old_version = obs.fields['backup'][VERSION_COLUMN]
                else:
                    old_version = obs.fields[VERSION_COLUMN]

                if old_version != fob.ob.fields[VERSION_COLUMN]:
                    raise FdbException(EFdbErrors.EFDB_CONFLICT_DURING_COMMIT,
                                       f"object {key_str} version mismatch")
                new_version = W32.inc_and_get_val(int
                                    (fob.ob.fields[VERSION_COLUMN]))
                fob.ob.fields[VERSION_COLUMN] = new_version

                fob.ob.state = EObState.PRESENT

        ob_str = fob.to_store_str()
        host = self.fdb.hostname
        gCon.log(f"[blue]{host} => Set {key_str} = {ob_str}[/blue]")
        self.fdb.db.set(key_str, ob_str)


    def t_rollback(self):
        gCon.rule(f"ROLLBACK! {self.tid}")
        self._return_all_borrows()
        self._remove_all_maps()


    def _remove_all_maps(self):
        self.created_uris.clear()
        self.locked_uris.clear()
        self.deleted_uris.clear()
        self.read_uris.clear()


    def _commit_pass(self):
        self._do_deletes()

        self._do_updates()

        self._do_creates()
       

    def t_commit(self):
        try:
            self._check_read_consistency()

            self.do_mod_db = False
            while True:
                self.chain_deletes = False
                self._commit_pass()
                if self.chain_deletes == True:
                    continue
                if (self.do_mod_db == True):
                    break
                self.do_mod_db = True

            self.fdb.db.commit()
            self._remove_all_maps()
            return

        except FdbException as fdbex:
            fdex = fdbex

        except Exception as ex:
            traceback.print_exc()
            fdex = FdbException(EFdbErrors.EFDB_INTERNAL_ERROR, str(ex)) 

        self.fdb.db.rollback()
        raise fdex


    def new_ob(self, fob):
        key_uri = fob.uri.unparse(True)
        self.created_uris[key_uri] = fob


    def update_detached_ob(self, detached_ob):
        key_uri = detached_ob.uri.unparse(True)

        if self.deleted_uris.get(key_uri) is not None:
            raise FdbException(EFdbErrors.EFDB_DELETED_OBJECT, key_uri)

        if self.read_uris.get(key_uri) is not None:
            raise FdbException(EFdbErrors.EFDB_CONFLICT_DURING_UPDATE, key_uri)

        if self.created_uris.get(key_uri) is not None:
            raise FdbException(EFdbErrors.EFDB_CONFLICT_DURING_UPDATE, key_uri)

        self.locked_uris[key_uri] = detached_ob


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


    def downvote_deleted_ob(self, uri_str_complete):
        uri_ob = self.fdb.parse_uri(uri_str_complete)
        uri_ob_local = self.fdb.remove_localhost(uri_ob)
        uri_str = uri_ob_local.unparse()
        gCon.log(f"I have to search {uri_str} to downvote")

        if self.deleted_uris.get(uri_str) is not None:
            return

        if self.read_uris.get(uri_str) is not None:
            raise FdbException(EFdbErrors.EFDB_NO_LOCK_ON_OB, uri_str)

        locked_ob = self.locked_uris.get(uri_str)
        if locked_ob is not None:
            gCon.log(f"Found object to downvote {uri_str}")
            locked_ob._dec_ref_ob()
            self.chain_deletes = True
            return

        created_ob = self.created_uris.get(uri_str)
        if created_ob is not None:
            gCon.log(f"Found created object to downvote {uri_str}")
            created_ob._dec_ref_ob()
            self.chain_deletes = True
            return

        raise FdbException(EFdbErrors.EFDB_MISSING_LINK_TO_DELETED_OB, uri_str)


    def get_ob(self, rctx):

        if self.deleted_uris.get(rctx.uri_str) is not None:
            raise FdbException(EFdbErrors.EFDB_NO_SUCH_OB)

        if rctx.must_lock:
            exist_val = self.locked_uris.get(rctx.uri_str)
            if exist_val is not None:
                return exist_val
        else:
            exist_val = self.read_uris.get(rctx.uri_str)
            if exist_val is not None:
                return exist_val

        maybe_created = self.created_uris.get(rctx.uri_str)
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
    only_local: bool = False
    internal_read: bool = False
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
        self.run_enabled = False
        async with self.stop_signal:
            self.stop_signal.notify_all()
        await self.ses_worker
        self.db.close()
        self.fact.reset()


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
            raise FdbException(EFdbErrors.EFDB_URI_EXISTS, uri)


    def new_ob_uri(self, t_id, uri, fields = {} ):
        registrar = self.fact.get_registrar(uri.ob_type)
        if registrar is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_TYPE)

        return self.new_ob_from_uri(t_id, registrar, uri, fields)


    def new_ob(self, t_id, ob_type, name, *, fields = {} , **kwargs):
        registrar = self.fact.get_registrar(ob_type)
        if registrar is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_TYPE, ob_type)

        uri = self.fact.uri_constructor(ob_type, name, **kwargs)

        return self.new_ob_from_uri(t_id, registrar, uri, fields)


    def parse_uri(self, uri_str):
        parse_fn = getattr(self.fact.uri_constructor, 'parse')
        uri_ob = parse_fn(uri_str)
        return uri_ob


    def return_object(self, key, ob = None):
        self.background_tasks += 1
        self.fdbtg.create_task(FederatedStore.return_object_task(self, key, ob))


    async def return_object_task(self, key, ob):
        try:
            await self.return_object_task_try(key, ob)
            gCon.log(f"[red]Returned object ok, I delete the key {key}[/red]")
            self.db.del_key(key)
            self.db.commit()
        except Exception as ex:
            traceback.print_exc()
            gCon.log(f"Got exception {ex} in return object!")
        finally:
            self.background_tasks -= 1
            async with self.stop_signal:
                self.stop_signal.notify_all()


    async def return_object_task_try(self, key, ob):
        social_api = self.kernel.get_dep(Dependencies.SOCIAL_API)
        if ob is not None:
            host = ob.uri.host
            ob_str = ob.to_store_str()
            res = await social_api.remote_req('fdb', 'return', host,
                        uri_str = key, obstr = ob_str)
        else:
            uri_ob = self.parse_uri(key)
            host = uri_ob.host
            gCon.log(f"===================== returned no mod {key} which is {host} ========")
            res = await social_api.remote_req('fdb', 'return_no_mod', host,
                        uri_str = key)


    def new_ob_from_uri(self, t_id, registrar, uri, fields):
        t_ob = self.get_tob_safe(t_id)

        uri = self.remove_localhost(uri, True)
        self.ensure_uri_not_existing(t_ob, uri)
        uri.host = self.hostname

        fob = FederatedObject(uri, registrar, fields = fields, locked = True)
        t_ob.new_ob(fob)

        return weakref.ref(fob)


    def uri_snapshot(self, uri_ob):
        """ read a snapshot of an object, from this object you CANNOT modify the DB """
        pass


    def remove_localhost(self, uriob, enforce = False):
        if uriob.host is None:
            return uriob
        if ((uriob.host == self.hostname) or
            (uriob.host == '::1') or
            (uriob.host == 'localhost') or
            (uriob.host == '127.0.0.1')):
            copied_uri = copy.copy(uriob)
            copied_uri.host = None
            return copied_uri
        if enforce == True:
            raise FdbException(EFdbErrors.EFDB_ONLY_LOCAL_STORE, uriob.host)
        return uriob


    async def _read_remote_ctx(self, rctx):
        host = rctx.uri_ob.host
        social_api = self.kernel.get_dep(Dependencies.SOCIAL_API)
        res = await social_api.remote_req('fdb', 'borrow', host, uri_str =
                    rctx.uri_str, lock = rctx.must_lock)
        remote_ob_str = res['obstr']
        return remote_ob_str


    async def return_object_received(self, t_id, uri_str, obstr = None):
        rctx = await self._uri_read_str_impl(t_id, uri_str, only_local = True,
                                     internal_read = True, must_lock = True)
        if rctx.fob.ob.state != EObState.LENT:
            raise FdbException(EFdbErrors.EFDB_INVALID_STATE)

        rctx.fob.returned_object(obstr)


    async def _read_ctx(self, rctx):
        rctx.tob = self.get_tob_safe(rctx.t_id)
        uri_local = self.remove_localhost(rctx.uri_ob,
                    rctx.only_local)

        rctx.uri_str = uri_local.unparse()
        rctx.fob = rctx.tob.get_ob(rctx)
        if rctx.fob is not None:
            return

        t_ob_str = self.db.get_maybe(rctx.uri_str) 
        new_state = None
        if ((t_ob_str is None) and (uri_local.host is not None)):
            t_ob_str = await self._read_remote_ctx(rctx)
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
        if rctx.uri_ob.host is None:
            rctx.uri_ob.host = self.hostname
        rctx.fob = str_to_fob(rctx.uri_ob, registrar, t_ob_str,
                              rctx.must_lock)

        if ((rctx.fob.ob.state == EObState.LENT) and 
            (rctx.internal_read == False)):
            gCon.log(f"{self.hostname}: Object {rctx.uri_str} has been lent!")
            raise FdbException(EFdbErrors.EFDB_LENT, f"{rctx.uri_str} lent to {rctx.fob.ob.fields}")

        if new_state is not None:
            rctx.fob.ob.state = new_state
        rctx.tob.read_ob_ctx(rctx)


    async def uri_read_lock(self, t_id, uri_ob, maybe = False):
        rctx = FedStore_ReadCtx(uri_ob, t_id, must_lock = True, maybe = maybe) 
        await self._read_ctx(rctx)
        return weakref.ref(rctx.fob)


    async def _uri_read_str_impl(self, t_id, uri_str, **kwargs):
        uri_ob = self.parse_uri(uri_str)
        return await self._uri_read_ob_impl(t_id, uri_ob, **kwargs)


    async def _uri_read_ob_impl(self, t_id, uri_ob, **kwargs):
        rctx = FedStore_ReadCtx(uri_ob, t_id, **kwargs) 
        await self._read_ctx(rctx)
        return rctx


    async def uri_read_str(self, t_id, uri_str, **kwargs):
        uri_ob = self.parse_uri(uri_str)
        return await self.uri_read_ob(t_id, uri_ob, **kwargs)


    async def uri_read_ob(self, t_id, uri_ob, **kwargs):
        rctx = await self._uri_read_ob_impl(t_id, uri_ob, **kwargs)
        if rctx.fob is None:
            return None
        return weakref.ref(rctx.fob)


    async def uri_read_no_lock(self, t_id, uri_ob, maybe = False):

        rctx = FedStore_ReadCtx(uri_ob, t_id, must_lock = False, maybe = maybe) 
        await self._read_ctx(rctx)
        if rctx.fob is None:
            return None
        return weakref.ref(rctx.fob)


    def update_detached_ob(self, t_id, detached_ob):
        tob = self.get_tob_safe(t_id)
        tob.update_detached_ob(detached_ob)


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

