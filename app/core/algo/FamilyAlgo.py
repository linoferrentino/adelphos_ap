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

# the algorithmic part for the families.

from app.core.model.FamilyFob import FamilyFob

class FamilyAlgo:


    def __init__(self, kernel):
        self.kernel = kernel 


    def exists_family(self, family_name):

        uri_fam = FamilyFob.get_uri(family_name)

        return False



