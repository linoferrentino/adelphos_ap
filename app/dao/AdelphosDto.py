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




# this is an abstract class.
@dataclass
class AdelphosDto:

    # every object in adelphos has the possibility to have a human name
    # the id is like the IP the name is like a DNS name
    # this could be None
    name: str

    # every object has an instance associated, local objects have the
    # 'None' instance which is the local one.
    instance_id: int

    # every object in adelphos has a local id.
    # this is given by the db engine.
    adelphos_id: int = None

    # the timestamp of this object, created.
    time_created: str = None 


    # every adelphos object has a residence (the place --- instance ---
    # where it is born), but can be cloned in other places, other adelphos
    # instances.

    def export_to(ctx, instance_uri):
        pass


    def import_from(ctx):
        pass


# the base class for the data access to the federated db in adelphos.
# this class has the logic to query the other federated instances
# the serialized representation of a remote object or to give it
# to others.
class AdelphosObjectDao(ABC):


    # the context is needed because I need to know if the host is
    # the local host.
    def __init__(self, ctx):
        self.ctx = ctx


    # this method gets the object from this instance or, if not present,
    # it will go to the outside world.
    # the URI here is parsed.
    @abstractmethod
    async def get_from_uri(ctx, uri):
        pass


    def _get_local_uri(uri):
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

