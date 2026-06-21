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
from app.federation.LifespanAware import LifespanAware
from app.sdc.Dependency import Dependency
from app.federation.SocialListener import SocialListener
from app.sdc.Dependencies import Dependencies
from app.logging import gCon
from app.cli.CliParser import CliParser


#class Kernel(Dependency, LifespanAware):
class Kernel(Dependency):
    #class Kernel(Dependency, LifespanAware, SocialListener):

    #def __init__(self, vhost, social_name):
    def __init__(self, vhost):
        super().__init__(vhost)
        #self.social_name = social_name


    def get_syscalls(self, syscall_type):
        match syscall_type:
            case 'cli':
                return self.get_cli_syscalls()
            case 'social':
                return self.get_social_syscalls()
            case _:
                raise Exception(f"invalid syscall req {syscall_type}")


    #@abstractmethod
    #def get_social_api_calls(self):
    #    pass


    @abstractmethod
    def get_cli_syscalls(self):
        pass


    @abstractmethod
    def get_social_syscalls(self):
        pass


    #async def start_async(self):
    #    #gCon.log(f"{id(self)} ============================= START ASYNC")
    #    #social = self.vhost.get_dep(Dependencies.SOCIAL)
    #    #social.add_listener(self.social_name, self)
    #    #gCon.log(f"Registered user {self.social_name}")
    #    pass


    #async def stop_async(self):
    #    #gCon.log(f"{id(self)} ============================= STOP ASYNC")
    #    #social = self.vhost.get_dep(Dependencies.SOCIAL)
    #    #social.remove_listener(self.social_name)
    #    pass


    #async def new_post(self, actor_from, msg):
    #    #gCon.log(f"got msg from {actor_from} {msg}")
    #    #cp = CliParser(msg)
    #    #gCon.log(f"These are the params {cp}")
    #    #social_api = self.vhost.get_dep(Dependencies.SOCIAL_API)
    #    #await social_api.new_post()
    #    pass



