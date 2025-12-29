# the data transfer for the cached actor.


from dataclasses import dataclass


@dataclass
class CachedActorDto:
    actor_id: int = 0
    ext_name: str = None
    inbox: str = None
    public_key: str = None
    date_created: str = None
