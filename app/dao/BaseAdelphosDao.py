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

# the abstract base dao for all the Adelphos Daos
from abc import ABC
from abc import abstractmethod
from ..logging import gCon
from dataclasses import asdict
from app.dao.BaseDao import BaseDao
from app.api.AdelphosException import AdelphosException
from app.api.AdelphosException import adelphos_ok_or_die
from app.api.AdelphosException import EAdelhposErrno


# This is the base class for all the objects in the federated
# database, either alive or inanimated.
class BaseAdelphosDao(BaseDao):


    # I store here the federated table name and its columns
    def __init__(self, dao):
        super().__init__(dao)


    def _is_local_uri(self, uri):
        if uri.host_name is None:
            return True

        if (uri.host_name == self.dao.app.get_local_host()):
            return True

        return False


    # `local' here means in the local db, but the object could be remote and cached here!
    def _try_get_local(self, uri):

        # I query from the local db, but the uri could be not local!
        if self._is_local_uri(uri):
            instance_fk = 0
        else:
            # I have to get the adelphos instance.
            instance_pack = self.dao.ad_instance_dao.get_from_hostname(uri.host_name, True)
            if instance_pack is None:
                # This is fatal. The server is not existing, so it cannot be here the object
                #gCon.log(f"No adelphos @{uri.host_name} cached")
                return None
            instance_fk = instance_pack.instance.actor_fk


        # the first difference is between a numeric uri and a normal uri
        if (uri.is_numeric):
            return self._try_get_local_numeric_uri(uri, instance_fk)

        return self._try_get_local_human_uri(uri, instance_fk)


    # here it is abstract, because we have two bases, the fd_actor and the fd_object
    @abstractmethod
    def _try_get_local_numeric_uri(self, uri):
        pass


    @abstractmethod
    def _try_get_local_human_uri(self, uri):
        pass


    # this method will get the object from the federated db 
    async def _get_from_remote_uri(self, uri):
        # get remote adelphos instance
        instance_pack = self.dao.ad_instance_dao.get_from_hostname(uri.host_name)
        #gCon.log(f"got {instance_pack} as adelphos instance")

        if instance_pack is None:
            instance_pack = await self.dao.ad_instance_dao.discover_from_host_name(
                    uri.host_name)

        if instance_pack is None:
            return None

        if instance_pack.instance.authorized == 0:
            raise AdelphosException(None, 
                EAdelhposErrno.EREMOTE_ADELPHOS_NOT_AUTHORIZED)

        # I am authorized to go outside, is it existent?
        remote_dto_exists = await self.dao.app.ad_gateway.ad_daemon_api.\
            exists_remote_uri(instance_pack, uri)

        if remote_dto_exists == False:
            return None

        # at this point I can create a placeholder for this URI in my local db.
        remote_dto = self._store_cached(instance_pack.instance.actor_fk, uri)
        return remote_dto


    # this method stores a cached version of the object, it is remote by definition.
    def _store_cached(self, instance_id, uri):

        adelphos_ok_or_die(not self._is_local_uri(uri))

        # OK, the uri is present, and also the instance is present.
        # the base_id could be a tuple, as in the case of the alias, which
        # has two base objects.
        dto = self._store_base_cached(instance_id, uri)
        return dto

    
    # this method gets the object from this instance or, if not present,
    # it will go to the outside world.
    # the URI here is parsed.
    #@abstractmethod
    # if maybe is True we don't complain if the object is not found.
    async def get_from_uri(self, uri, no_route = False, maybe = False):

        # first of all I try to know if this object is present in my db, remote or not
        # this function is not async, because I do not leave the instance.
        dto = self._try_get_local(uri)

        if (dto is not None):
            return dto

        if no_route == True:
            gCon.log(f"uri {uri} is not present locally, but no_route is True")
            return None

        # I have not found it, if the uri is local this is a not recoverable error
        local_uri = self._is_local_uri(uri)

        if local_uri == False:
            #gCon.log(f"Uri {uri} not local, go to fediverse!")
            # I try to get the object from the federated db
            dto = await self._get_from_remote_uri(uri)
    
            if (dto is not None):
                return dto
        else:
            # this is an error.
            raise AdelphosException(f"Cannot route uri {uri} without hostname", 
                                    EAdelhposErrno.ENOROUTEFORURI)
            
        if (maybe == True):
            return None

        raise AdelphosException(f"Could not find URI {uri}", 
                                EAdelhposErrno.EURI_NOT_FOUND)


    # I can query the adelphos db using the local name. All objects in adelphos
    # have a name, the exception is the alias that has also the family.
    def get_from_local_name(self, name):
        pass



    # The local uri needs to query the raw_view table.
    def _get_local_numeric_uri(ctx, uri):
        pass


    # this method forces the locality of this uri, of course it must be
    # local: the function is sync, as it needs not to go to the outside.
    def get_object_local(self, ctx, uri):

        if (uri.host_name is not None):
            if (uri.host_name != ctx.app.config['General']['Host']):
                raise AdelphosException(f"uri {uri} is not local")

        return self._get_local_uri(ctx, uri)


    def _get_local_uri(self, ctx, uri):

        # OK, now I can grab the adelphos object.

        # if the URI is local then I need to differentiate between
        # a mechanical uri and a text one
        if (uri.is_numeric):
            return _get_local_numeri_uri(uri)

        return _get_local_human_uri(uri)


    # the remote uri could be locally cached.
    def _get_remote_uri(uri):
        # first of all I have to get the instance object.
        # then with the instance object I can query the local
        # table to see if the object is cached, otherwise
        # I will go outside.

        # query the instance

        pass


    # this checks that the uri is of the right type and then it
    # will perform the actual search in the local DB or in the
    # external one.
    def _get_from_uri_base(uri, needed_type):
        if (uri.obj_type != needed_type):
            raise AdelphosException(f"This URI belongs to type \
{uri.obj_type} but I needed {needed_type}")

        # OK, the URI is of the right type. Is it local?
        if (uri.host_name is None):
            return _get_local_uri(uri)

        return _get_remote_uri(uri)


    #@abstractmethod
    def get_from_uri_str(uri):
        pass


    # creates a dto from a uri (using the initialization provided)
    # the arguments are passed to the dto constructor
    def create_from_uri(self, uri, *args, **kvargs):
        pass


    # Not all objects have a default constructor, so this might fail
    #@abstractmethod
    def get_or_create_from_uri(uri):
        pass


