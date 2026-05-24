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


from app.federation.FederatedFactory import FederatedFactory

def adelphos_schema():

    FederatedFactory.set_uri_constructor(AdelphosUri)

    FedeObClass1.register_class()
    FedeObClass2.register_class()


