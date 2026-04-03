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

from app.store.AdelphosStore import AdelphosStore

# the memory store in adelphos


class MemoryStore(AdelphosStore):


    def __init__(self):

        self.families_by_id = {}
        self.families_by_name = {}
        self.next_family = 1

        self.aliases_by_id = {}
        self.aliases_by_name = {}
        self.next_alias = 1



    # here it is a no-op
    def rollback(self):
        pass
