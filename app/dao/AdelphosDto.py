# this is the base class for all the objects in adelphos

from dataclasses import dataclass

from app.dao.InstanceDto import InstanceDto


# the format of an adelphos URI is dependent on the type
# for the alias, the URI is simplified as`

# this is the mechanical URI
# $<type>$<local_id>@<host>



# I can query the database as this.

# then I have the human URI

# for example an alias is
# -alias@host in human form
# 
# the single @ is for a local alias
# alias

# this is a currency
# #cu#euro@www.adelphos.it

# this is a group
# #gr#terrible_cats@www.adelphos.it

# a family (a group of level zero)
# #gr0#ferrentino@www.adelphos.it

# this is a place
# #pl#stadium_north@www.adelphos.it

# this is an item.
# #ob#used_pc99@www.adelphos.it


# this is an abstract class.
@dataclass
class AdelphosDto:

    # every object in adelphos has a local id.
    local_id: int = None

    # every object in adelphos has the possibility to have a human name
    # the id is like the IP the name is like a DNS name
    human_name: str = None

    # every object has an instance associated, local objects have the
    # 'None' instance which is the local one.
    instance_id: int = None

    time_created: str = None 

    time_cloned: str = None

    # every adelphos object has a residence (the place --- instance ---
    # where it is born), but can be cloned in other places, other adelphos
    # instances.

    def export_to(ctx, instance_uri):
        pass


    def import_from(ctx):
        pass

