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


    def __init__(self, method, query_params, path_params,
                 json_ob, urlp, headers = None):


        if (json_ob is not None) and (isinstance(json_ob, dict) == False):
            raise Exception(f"I am expeting an object here got {json_ob}")

        gCon.log(f"create req json /{json_ob}/ urlp {urlp} headers {headers}")

        self.method = method
        self.query_params = { k: v[0] for k, v in query_params.items() }
        self.path_params = path_params 
        self._inner_json = json_ob
        self.json = self.get_json 
        self.headers = headers if headers is not None else {}
        self.url = urlp
        self.client = ""
        self._inner_body = json.dumps(json_ob).encode('utf-8')
        self.body = self.get_body


    async def get_json(self):
        return self._inner_json


    async def get_body(self):
        return self._inner_body



