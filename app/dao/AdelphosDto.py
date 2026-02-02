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
# this is the base class for all the objects in adelphos


from dataclasses import dataclass
from abc import ABC
from abc import abstractmethod
from app.dao.InstanceDto import InstanceDto




# this is an abstract class, this is the base class for all the
# inanimate objects in adelphos
@dataclass
class AdelphosDto:

    # every object in adelphos has the possibility to have a human name
    # the id is like the IP the name is like a DNS name
    # this could be None
    name: str

    # the creator is an alias
    creator_fk: int

    # every object in adelphos has a local id.
    # this is given by the db engine.
    adelphos_id: int = None

    # the timestamp of this object, created.
    time_created: str = None 


    #def export_to(ctx, instance_uri):
    #    pass


    #def import_from(ctx):
    #    pass


# the base class for the data access to the federated db in adelphos.
# this class has the logic to query the other federated instances
# the serialized representation of a remote object or to give it
# to others.
class AdelphosObjectDao(ABC):


    # every federated table in the db has a 1:1 mapping with the
    # adelphos object table. Here we have the common code.
    def __init__(self, dao):
        self.dao = dao 


    # this method gets the object from this instance or, if not present,
    # it will go to the outside world.
    # the URI here is parsed.
    @abstractmethod
    async def get_from_uri(ctx, uri):
        pass


    # this method forces the locality of this uri, of course it must be
    # local.
    def get_object_local(ctx, uri):

        if (uri.host_name is not None):
            if (uri.host_name != ctx.app.config['General']['Host']):
                raise AdelphosException(f"uri {uri} is not local")

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


    @abstractmethod
    def get_from_uri_str(uri):
        pass


    # Not all objects have a default constructor, so this might fail
    @abstractmethod
    def get_or_create_from_uri(uri):
        pass

