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

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass


# the federated uri is the common base for the federated
# identifiers into the federated store.
# The uri can be decomposed in four main parts

# object type
# name
# family (*)
# host   (*)
# fragment (*)

# all the fields marked as (*) are optional.
# if host is not present it is considered local
# if fragment is not present it is considered global
# if family is not present than the name is all there is.


@dataclass
class FederatedUri(ABC):

    ob_type: str
    name: str
    family: str = None
    host: str = None
    fragment: str = None

    # returns a string representation used to put as a key in db
    @abstractmethod
    def unparse(self) -> str:
        pass


    


