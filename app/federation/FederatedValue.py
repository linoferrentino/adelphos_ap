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


# the class which holds a federated object in the DB
class FederatedValue:


    # every object starts at version zero and then we increment it.
    # when it is locked it cannot 
    def __init__(self, ob):
        self.inner = ob
        self.version = 0
        # timestamp of the lock, used to prevent deadlocks.
        self.ts_locked = None
        self.locked = False


    async def get(self):
        return None


    # the store is not async, we store locally (fast) and then try
    # to synchronized the federated adelhpoi.
    def store(self, ob):
        pass
