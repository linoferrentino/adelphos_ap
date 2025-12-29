

from dataclasses import dataclass

# This is the class which models an alias in adelphos, usually this is a
# real person in the fediverse.

@dataclass
class AliasDao:
    alias_id: int = 0
    actor_id: int = 0
    alias: str = None
    password: str = None
    date_created: str = None
