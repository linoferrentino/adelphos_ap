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


from abc import ABC, abstractmethod
from app.sdc.Dependencies import Dependencies
from app.federation.BaseSocial import BaseSocial
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from app.logging import gCon




class SimpleSocial(BaseSocial):

    def __init__(self, vhost):
        super().__init__(vhost)







   



