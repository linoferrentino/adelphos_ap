

from dataclasses import dataclass

# This is the class which models an alias in adelphos, usually this is a
# real person in the fediverse.

@dataclass
class AliasDao:

    alias_id: int = 0
    alias: str = None
    ext_name: str = None
    inbox: str = None
    password: str = None
    public_key: str = None
