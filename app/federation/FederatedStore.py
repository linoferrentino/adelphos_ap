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

class FederatedStore:



    # this adds a federation host able to share values with myself.
    def add_federation_host(self, host):
        pass


    def remove_federation_host(self, host):
        pass


    def get_uri_read(self, uri):
        pass


    def get_uri_write(self, uri):
        pass


    # the store has the concept of a federated transaciton
    def begin_transaction(self):
        pass


    def get_and_lock_ob_uri(self, transaction_id, uri, maybe = False):
        pass


    def commit_transaction(self, transaction_id):
        pass


    def rollback_transaction(self, transaction_id):
        pass

