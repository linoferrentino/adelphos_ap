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

import re

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import KW_ONLY
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno

from app.logging import gCon


@dataclass
class FederatedUri(ABC):

    ob_type: str
    name: str
    _ : KW_ONLY
    host: str = None
    fragment: str = None


    @abstractmethod
    def unparse(self, force_local = False):
        pass


    def _base_get_host_part(self):
        return f"@{self.host}" if self.host is not None else ""


    @staticmethod
    def _divide_local_host_part(uri):
        local_remote_splits = uri.split('@')
        if (len(local_remote_splits) > 2):
            raise AdelphosException(AdErrno.EINVALID_URI,
f"Illegal adelphos uri {uri} more than one '@'")
            
        if (len(local_remote_splits) == 2):
            host_part = local_remote_splits[1]
        else:
            host_part = None

        object_part = local_remote_splits[0]

        return (object_part, host_part)


    @staticmethod
    def create_uri(uri_type, object_part, *, host_part = None, fragment = None):
        assert False


    @classmethod
    def divide_type_name(cls, object_part):
        type_name_match = re.match(
r"#([a-z0-9\.-_]{2})#([^#]*)$", object_part)

        if (type_name_match is None):
            raise AdelphosException(AdErrno.EINVALID_URI, 
f"Illegal URI {object_part} I was expecting something like #<type>#<name>")

        uri_type = type_name_match.group(1)
        name_part= type_name_match.group(2)

        return (uri_type, name_part)


    @classmethod
    def parse(cls, uri):

        (object_part, host_part) = FederatedUri._divide_local_host_part(uri)

        (uri_type, name_part) = cls.divide_type_name(object_part)

        uri_ob = cls.create_uri(uri_type, name_part, host_part = host_part)

        return uri_ob


