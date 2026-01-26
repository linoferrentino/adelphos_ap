# this is the data class that holds the data relative to an instance



from app.dao.ActorDto import ActorDto
from dataclasses import dataclass


@dataclass
class InstanceDto:

    instance_id: int = 0

    # the instance has the link to an actor which is the end point
    endpoint: ActorDto = None

    # we could have various level of trust
    authorized: bool = True



# the Instance table is different from the other objects because
# it has not a uri, the table is not federated like the others.
class InstanceDao:


    
    def get_from_host(host_name):
        pass
