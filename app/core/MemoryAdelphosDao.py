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

# the memory DAO will store the data in memory.


from app.core.AdelphosDao import AdelphosDao


class MemoryAdelphosDao(AdelphosDao):


    def __init__(self):
        self.families = {}
        self.next_family = 1
        self.aliases = {}
        self.next_alias = 1


    def get_family(self, family):
        pass


    def add_family(self, family):
        fam_id = self.next_family
        self.next_family += 1
        self.families[fam_id] = { 'name' : family }
        return fam_id
    

    def add_alias(self, alias, fam_id):
        alias_id = self.next_alias
        self.next_alias += 1
        self.aliases[alias_id] = { 'name' : alias, 'fam_fk': fam_id }
        return alias_id
