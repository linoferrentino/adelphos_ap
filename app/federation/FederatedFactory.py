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

# the base class that can create the objects in a federated store:

from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors
from dataclasses import dataclass


@dataclass
class FederatedFactoryRegistrar:
    
    constructor : callable
    first_class : bool
    needs_family : bool


class FederatedFactory:

    registrars = dict()
    uri_constructor = None

    # TODO 
    #schema_id = None
    #schema_version = None


    @classmethod
    def set_uri_constructor(cls, uri_const):
        cls.uri_constructor = uri_const


    def __init__(self):
        raise Exception("Not instantiable")


    @classmethod
    def _register_ob_type(cls, type_str, registrar):
        cls.registrars[type_str] = registrar


    @classmethod
    def get_registrar(cls, uri_type):
        registrar = cls.registrars.get(uri_type)
        return registrar


