######################################################
#
# Adelphos AP: the fractal trust network
#
# Activity Pub implementation
#
# © 2026 Lino Ferrentino
# lino.ferrentino@gmail.com
#
# This is free software. Licensed with GPL version 3
#
######################################################
#
# this is the base class for all the objects in adelphos


from dataclasses import dataclass

from app.dao.InstanceDto import InstanceDto




# this is an abstract class.
@dataclass
class AdelphosDto:

    # every object in adelphos has the possibility to have a human name
    # the id is like the IP the name is like a DNS name
    # this could be None
    name: str

    # every object has an instance associated, local objects have the
    # 'None' instance which is the local one.
    instance_id: int

    # every object in adelphos has a local id.
    # this is given by the db engine.
    adelphos_id: int = None

    # the timestamp of this object, created.
    time_created: str = None 


    # every adelphos object has a residence (the place --- instance ---
    # where it is born), but can be cloned in other places, other adelphos
    # instances.

    def export_to(ctx, instance_uri):
        pass


    def import_from(ctx):
        pass

