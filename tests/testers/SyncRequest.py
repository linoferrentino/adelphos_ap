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

class SyncRequest:


    def __init__(self, query_params, path_params, json):

        self.query_params = query_params
        self.path_params = path_params 
        self._inner_json = json
        self.json = self.get_json 


    async def get_json(self):
        return self._inner_json


    #async def json(self):
    #    return self.json 


