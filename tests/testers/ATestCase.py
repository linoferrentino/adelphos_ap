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

import yaml
from abc import ABC
from abc import abstractmethod

from app.logging import gCon

class ATestCase:

    def __init__(self, world_setup, world_verifier):
        self.world_setup = world_setup
        self.world_verifier = world_verifier


    def setup(self, world):
        #world_conf = yaml.safe_load(self.world_setup)
        #gCon.log(f"Set up the world {world_conf}")
        pass

    
    def pre_conditions(self):
        gCon.log(f"Pre conditions")


    def do_actions(self):
        gCon.log(f"Do actions")


    def verify(self):
        gCon.log(f"Verify")

