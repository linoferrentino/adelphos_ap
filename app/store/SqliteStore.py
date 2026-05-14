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


import sqlite3

from app.store.SimpleKvStore import SimpleKvStore
from app.dao.AdelphosDb import AdelphosDb


# Source - https://stackoverflow.com/a/47240886
# Posted by Basj, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-13, License - CC BY-SA 4.0
class KeyValueStore(dict):


    def __init__(self, conn):
        #self.conn = sqlite3.connect(filename)
        self.conn = conn
        self.conn.execute("CREATE TABLE IF NOT EXISTS kv (key text unique, value text)")


    #def close(self):
    #    self.conn.commit()
    #    self.conn.close()


    def commit(self):
        self.conn.commit()


    def rollback(self):
        self.conn.rollback()


    def __len__(self):
        rows = self.conn.execute('SELECT COUNT(*) FROM kv').fetchone()[0]
        return rows if rows is not None else 0


    def iterkeys(self):
        c = self.conn.cursor()
        for row in c.execute('SELECT key FROM kv'):
            yield row[0]


    def itervalues(self):
        c = self.conn.cursor()
        for row in c.execute('SELECT value FROM kv'):
            yield row[0]


    def iteritems(self):
        c = self.conn.cursor()
        for row in c.execute('SELECT key, value FROM kv'):
            yield row[0], row[1]


    def keys(self):
        return list(self.iterkeys())


    def values(self):
        return list(self.itervalues())


    def items(self):
        return list(self.iteritems())


    def __contains__(self, key):
        return self.conn.execute('SELECT 1 FROM kv WHERE key = ?', (key,)).fetchone() is not None


    def __getitem__(self, key):
        item = self.conn.execute('SELECT value FROM kv WHERE key = ?', (key,)).fetchone()
        if item is None:
            raise KeyError(key)
        return item[0]


    def __setitem__(self, key, value):
        self.conn.execute('REPLACE INTO kv (key, value) VALUES (?,?)', (key, value))


    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        self.conn.execute('DELETE FROM kv WHERE key = ?', (key,))


    def __iter__(self):
        return self.iterkeys()


class SqliteStore(SimpleKvStore):

    def __init__(self, store_file = ":memory:"):
        #self.__kv = KeyValueStore(store_file)
        self.__kv = None
        self.__db = None
        pass


    def commit(self):
        pass


    def rollback(self):
        pass


    #def open(self, conn_string):
    #    pass


    #def close(self):
    #    pass


    def set(self, key, value):
        pass


    def get(self, key):
        pass


    def get_maybe(self, key):
        pass

    
    def has_key(self, key):
        pass


    def del_key(self, key):
        pass
