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

from app.store.AdelphosStore import AdelphosStore


# the FederatedStore uses the transport to access objects which
# are beyond its reach and to perform a distributed commit.


# open uri 
# #al#lino.ferre@adelphos.it#objects.link
# the uri can have a fragment, this will lock only the corresponding part.


# the database can have the possibility to know the value of the link

# the store has a router it is needed to do remote queries.

from app.transport.RouterProvider import RouterProvider

class FederatedStore(RouterProvider):


    # I initialize myself with my hostname to distinguish my own URIs from the others.
    def __init__(self, hostname, db, transport):

        self.db = db
        self.transport = transport
        # you can use a federated store like a local store, in this case
        if transport is not None:
            transport.register_routes(self)


    def get_async_router(self):
        pass


    def register_sync_routes(self, router):
        pass


    # this adds a federation host able to share values with myself.
    def add_federation_host(self, host):
        pass


    def remove_federation_host(self, host):
        pass


    #def get_uri_read(self, uri):
    #    pass


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


    def commit(self):
        self.db.commit()


    def rollback(self):
        self.db.rollback()


    def close(self):
        self.db.close()


    # opens an URI not for update. It will not be part of the transaction, the result
    # is a FederatedValue
    def open_uri_maybe(self, uri_str):
        pass


    # opens the URI passing it as an object.
    def open_uri_ob_maybe(self, uri):
        pass


    # gets the object associated with this uri string.
    # if maybe is True it does not 
    def open_fv_from_uri_str(self, uri_str, maybe = False, 
                     only_local = False, lock = False, create_if_not_exist = False):
        pass


    # this is a transaction: update a certain number of federated values.
    # the idea is to commit all the locked objects.
    # for now I do not see a use case where you should have a partial transaction.
    def commit(self):
        pass

    
    def rollback(self):
        pass


    #def set(self, key, value):
    #    self.db.set(key, value)


    #def update(self, ob):
    #    pass


    #def get_maybe(self, key):
    #    return self.db.get_maybe(key)


    # the store has the concept of a federated transaciton
    #def begin_transaction(self):
    #    pass


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


    #def commit_transaction(self, transaction_id):
    #    pass


    #def rollback_transaction(self, transaction_id):
    #    pass

