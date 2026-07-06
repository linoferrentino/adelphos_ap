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
from dataclasses import KW_ONLY


@dataclass
class FederatedUri(ABC):

    ob_type: str
    name: str
    _ : KW_ONLY
    #family: str = None
    host: str = None
    fragment: str = None


    @abstractmethod
    def unparse(self) -> str:
        pass


    @abstractmethod
    def parse(self, uri_str):
        pass
    


