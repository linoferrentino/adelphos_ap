# this is the base class for all the objects in adelphos

from dataclasses import dataclass

from app.dao.InstanceDto import InstanceDto


# this is an abstract class.
@dataclass
class AdelphosDto:
    # an object in adelphos has a global identifier (which is global in all
    # the instances) and various control fields to acquire it on demand.
    #object_uri: str = None

    # every object in adelphos has a local id.
    local_id: int = None

    # every object has an instance associated, local objects have the
    # 'None' instance which is the local one.
    instance: InstanceDto = None

    
    time_created: str = None 

    time_cloned: str = None


    # every adelphos object has a residence (the place --- instance ---
    # where it is born), but can be cloned in other places, other adelphos
    # instances.

    def export_to(ctx, instance_uri):
        pass


    def import_from(ctx):
        pass

