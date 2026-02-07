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


# This is the base class for all the objects in the federated
# database, either alive or inanimated.
class BaseAdelphosDao(ABC):


    # I store here the federated table name and its columns
    def __init__(self, db, ftbl, ftbl_col_list):
        self.db = db 
        self.ftbl = ftbl
        self.ftbl_col_list = ftbl_col_list


    # here there are the abstract methods common to all the
    # federated objects.
    
    # this method gets the object from this instance or, if not present,
    # it will go to the outside world.
    # the URI here is parsed.
    #@abstractmethod
    async def get_from_uri(ctx, uri):
        pass


    # I can query the adelphos db using the local name. All objects in adelphos
    # have a name, the exception is the alias that has also the family.
    def get_from_local_name(self, name):
        pass



    # The local uri needs to query the raw_view table.
    def _get_local_numeri_uri(ctx, uri):
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

