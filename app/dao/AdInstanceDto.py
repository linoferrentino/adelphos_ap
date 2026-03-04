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

# This is the object that holds the data of an adelphos instance.
# the adelphos instance is also an activity pub instance, but not the contrary

from dataclasses import dataclass

@dataclass
class AdInstanceDto:

    actor_fk: int
    authorized: int
    comment: str
    timestamp: str

    def get_pk(self):
        return self.actor_fk


# the function to create an instance with default fields
def create_ad_instance(actor_fk, authorized, comment):
    ad_instance = AdInstanceDto(actor_fk, authorized, comment, None)
    return ad_instance

