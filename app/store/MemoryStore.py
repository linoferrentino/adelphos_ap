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

from app.store.SimpleKvStore import SimpleKvStore

# the memory store in adelphos
# a simple key/value pair with transactions.
# inspired by 
# https://github.com/zackdever/vsims#
# here transactions do not nest, however


class Block:
    """A block of operations that can be called in reverse order.

    Use: To isolate a block of commands, before executing each command,
    log a command which will reverse it.
    Then if needed, simply rollback to undo that block.
    """
    def __init__(self):
        self.clear()


    def clear(self):
        self.ops = []


    def log(self, command, *args):
        """Adds the command and arguments to the log.

        command - a function that will be called on rollback
        args - arguments to be supplied to the command on rollback
        """
        self.ops.append((command, args))


    def rollback(self):
        """Call all the logged commands in reverse order."""
        for op in reversed(self.ops):
            op[0](*op[1])
        self.clear()


class MemoryStore(SimpleKvStore):


    def __init__(self):
        self.reset()


    def reset(self):
        self.undos = Block()
        self.store = {}


    def open(self):
        pass


    def set(self, key, value, doLog=True):
        has_key = self.has_key(key)

        if doLog:
            if has_key:
                self.undos.log(self.set, key, self.get(key), False)
            else:
                self.undos.log(self.delete, key, False)

        self.store[key] = value


    def get(self, key):
        """Returns the value of the given key.

        throws: KeyError if key is not present in the store
        """
        return self.store[key]


    def get_maybe(self, key):
        value = self.store.get(key)
        return value


    def has_key(self, key):
        """Determines if the store contains the key."""
        return key in self.store.keys()


    def del_key(self, key):
        self.delete(key)


    def delete(self, key, doLog=True):
        """Deletes the key from the store if present.

        key - key to delete
        doLog - determines if a reverse operation should be logged
        """
        if self.has_key(key):
            if doLog:
                self.undos.log(self.set, key, self.get(key), False)

            del self.store[key]
        else:
            raise KeyError(key)


    def commit(self):
        self.undos.clear()


    def rollback(self):
        self.undos.rollback()


    # a close automatically rollbacks the last transaction
    def close(self):
        self.rollback()
