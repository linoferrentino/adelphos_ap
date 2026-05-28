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


class SyncRequest:


    def __init__(self, query_params, path_params, json, urlp, headers = None):

        self.query_params = { k: v[0] for k, v in query_params.items() }
        self.path_params = path_params 
        self._inner_json = json
        self.json = self.get_json 
        self.headers = headers if headers is not None else {}
        self.url = urlp.geturl()
        self.client = ""


    async def get_json(self):
        return self._inner_json



