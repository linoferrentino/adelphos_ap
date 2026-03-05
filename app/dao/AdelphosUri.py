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

# The class that parses the URIs in adelphos.
# The URIs are used to identify objects in the federated database

from enum import StrEnum
from dataclasses import dataclass
import dataclasses
import re

from app.api.AdelphosException import AdelphosException
from app.logging import gCon


# the format of an adelphos URI is dependent on the type
# for the alias, the URI is simplified as`

# this is the mechanical URI
# #<type>#<local_id>@<host>

# the family (f0) does not exist independently from the alias.
# That is, the family has at least one alias.
# an empty family is not possible.

# I can query the database with this URI,
# the database is federated, I could see that
# object somewhere else, but usually it is located
# in the adelphos instance that has created it.

# then I have the human URI

# for example an alias is
# ##alias.family@host in human form
# or
# ##$392@host in mechanical form

# we might have also the alternative representation
# #al#alias.family@host
# or
# #al#$<ID>@host
# 
# the single string is for a local alias
# ##alias.family

# this is a currency in the fediverse
# #cu#euro@www.adelphos.it

# #cu#euro for a local currency

# this is a group
# #gr#terrible_cats@www.adelphos.it

# Or with the numeric ID
# #gr#$1818@www.adelphos.it

# a family (a group of level zero)
# #g0#ferrentino@www.adelphos.it

# this is a place
# #pl#stadium_north@www.adelphos.it

# this is an item.
# #ob#used_pc99@www.adelphos.it


# This enumeration will list all the types in the federated database
# with their compact representation (two letters).
class EAdelphosType(StrEnum):
    ALIAS_TYPE = 'al'
    CHEQUE_TYPE = 'cq'
    CURRENCY_TYPE = 'cu'
    FAMILY_TYPE = 'fa'
    GROUP_TYPE = 'gr'
    OBJECT_TYPE = 'ob'
    PLACE_TYPE = 'pl'
    TRANSIT_LINE = 'tr'
    TRUST_LINE = 'tl'


@dataclass
class AdelphosUri:

    obj_type: EAdelphosType
    is_numeric: bool
    host_name: str

    _ : dataclasses.KW_ONLY

    name: str = None
    # Only for the aliases we have a family
    family: str = None
    numeric_id: int = None



# to divide I have to look for a point
def _divide_uri_alias_family(object_part):

    alias_family_splits = object_part.split(".")
    if (len(alias_family_splits) > 2):
        raise AdelphosException(f"Illegal alias_family {alias_family}. \
Only one dot is allowed ")

    if (len(alias_family_splits) == 1):
        # the family is null.
        return (alias_family_splits[0], None)

    return alias_family_splits


def validate_local_name(local_name):

    # a NULL is valid (
    if (local_name is None):
        return

    if (re.match("[a-z0-9][a-z0-9_-]*[a-z0-9]+", local_name, 
                 re.IGNORECASE) is None):
        raise AdelphosException(f"Invalid name {local_name}, \
it must begin and end with a letter or a digit.")

    if (len(local_name) < 2 or len(local_name) > 64):
        raise AdelphosException(f"name {local_name} length incorrect")


# to parse the object part we need the uri_type, because not
# all the types can have the family part.
def _parse_object_part(object_part, uri_type):
    # I have to know if this is in mechanical or human form

    if (object_part[0] == '$'):
        # this is a mechanical form, so we have to remove the
        # dollar and see the integer inside.
        object_part = alias_family[1:]

        # maybe there are extraneous characters.
        if (re.match(r"\D", alias_family) is not None):
            raise AdelphosException(f"Illegal numeric id {alias_family}")

        mechanical_id = int(alias_family)

        return (None, None, mechanical_id)

     # this is human form, so we simply divide the name and family
    (alias, family) = _divide_uri_alias_family(object_part)

    if (uri_type == EAdelphosType.ALIAS_TYPE):
        if (family is None):
            raise AdelphosException(
f"An alias must have a family! {alias_match.group(1)} has not one.")
    else:
        if (family is not None):
            raise AdelphosException(
f"Illegal identifier {type_name_match.group(2)}: \
Only aliases can have a family.")

    # here I must validate the names
    validate_local_name(alias)
    validate_local_name(family)

    return (alias, family, None)


def _parse_uri_type(uri_type_str):

    match uri_type_str:
        case 'al':
            uri_type = EAdelphosType.ALIAS_TYPE
        case 'cq':
            uri_type = EAdelphosType.CHEQUE_TYPE
        case 'cu':
            uri_type = EAdelphosType.CURRENCY_TYPE
        case 'fa':
            uri_type = EAdelphosType.FAMILY_TYPE
        case 'gr':
            uri_type = EAdelphosType.GROUP_TYPE
        case 'ob':
            uri_type = EAdelphosType.OBJECT_TYPE
        case 'pl':
            uri_type = EAdelphosType.PLACE_TYPE
        case 'tr':
            uri_type = EAdelphosType.TRANSIT_LINE
        case 'tl':
            uri_type = EAdelphosType.TRUST_LINE
        case _:
            raise AdelphosException(f"Unknown type \
{type_name_match.group(1)}")

    return uri_type


# this function is used to parse an URI with the
# type already fixed.
# for example

def uriparse_type(uri, uri_type):

    (object_part, host_part) = _divide_local_host_part(uri)
    (name, family, mechanical_id) = _parse_object_part(object_part,
                                                           uri_type)

    # OK, now I can return the object
    return _create_parsed_uri(uri_type, object_part, host_part,
                              name, family, mechanical_id)


def _divide_local_host_part(uri):
    # first of all I need to know if this uri is local or remote.
    local_remote_splits = uri.split('@')
    if (len(local_remote_splits) > 2):
        raise AdelphosException(f"Illegal adelphos uri {uri} \
more than one '@'")
        
    if (len(local_remote_splits) == 2):
        host_part = local_remote_splits[1]

        # here I should know the current adelphos
        # instance's addresse
    else:
        host_part = None

    object_part = local_remote_splits[0]

    return (object_part, host_part)


def uriparse_type(uri, type_expected):
    uri_ob = uriparse(uri)
    if (uri_ob.obj_type != type_expected):
        raise AdelphosException(f"Expecting {type_expected} found {uri_ob.obj_type}")


# this function will parse an URI in adelphos and return the
# parsed object
# there is not much error handling (yet)
def uriparse(uri):

    (object_part, host_part) = _divide_local_host_part(uri)

    #Now we have to divide the object part.
    # first of all is it an alias?
    alias_match = re.match(r"##(.*)", object_part)

    if (alias_match is not None):

        uri_type = EAdelphosType.ALIAS_TYPE
        object_part = alias_match.group(1)
        (name, family, mechanical_id) = _parse_object_part(object_part,
                                                           uri_type)
    else:

        # this is an object, which has not a family
        # first of all we derive the type
        type_name_match = re.match(
r"#([a-z0-9\.-_]{2})#([^#]*)$", object_part)

        if (type_name_match is None):
            raise AdelphosException(f"Illegal URI {object_part} \
I was expecting something like #<type>#<name> or #<type>#$<id>")

        uri_type = _parse_uri_type(type_name_match.group(1))

        (name, family, mechanical_id) = _parse_object_part(
                type_name_match.group(2), uri_type)
    
    return _create_parsed_uri(uri_type, object_part, host_part,
                              name, family, mechanical_id)


def _create_parsed_uri(uri_type, object_part, host_name, name,
                       family, mechanical_id):


    # Ok now we can create the object
    if (mechanical_id is not None):
        adelphos_uri = AdelphosUri(uri_type,
                        True, host_name, numeric_id = mechanical_id)
    else:
        adelphos_uri = AdelphosUri(uri_type,
                        False, host_name, name = name, family = family)

    # return the parsed object
    return adelphos_uri


