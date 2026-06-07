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


from app.logging import gCon
import json


class SyncRequest:


    def __init__(self, query_params, path_params, json_ob, urlp, headers = None):

        gCon.log(f"create req json {json_ob} urlp {urlp}")

        self.query_params = { k: v[0] for k, v in query_params.items() }
        self.path_params = path_params 
        self._inner_json = json_ob
        self.json = self.get_json 
        self.headers = headers if headers is not None else {}
        self.url = urlp.geturl()
        self.client = ""
        self._inner_body = json.dumps(json_ob)
        self.body = self.get_body


    async def get_json(self):
        return self._inner_json


    async def get_body(self):
        return self._inner_body



