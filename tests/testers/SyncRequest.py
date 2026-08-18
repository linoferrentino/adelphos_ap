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
                 in_json, urlp, headers = None):


        #if (json_ob is not None) and (isinstance(json_ob, dict) == False):
        #    raise Exception(f"I am expeting an object here got {json_ob}")
        gCon.log(f"get {in_json} of type {type(in_json)} for url {urlp} headers {headers}")
        #assert ((json_str is None) or (isinstance(json_str, str)))
        #assert ((json_ob is None) or (isinstance(json_ob, dict)))
        if in_json is None:
            json_ob = None
            json_body = None
        elif isinstance(in_json, bytes):
            json_ob = json.loads(in_json)
            json_body = in_json
        elif isinstance(in_json, str):
            json_ob = json.loads(in_json)
            json_body = in_json.encode('utf-8')
        elif isinstance(in_json, dict):
            json_ob = in_json
            json_body = json.dumps(in_json, separators=(',',':')).encode('utf-8')
        else:
            gCon.log(f"invalid type {in_json}")
            assert False

        self.method = method
        self.query_params = { k: v[0] for k, v in query_params.items() }
        self.path_params = path_params 
        self._inner_json = json_ob
        self.json = self.get_json 
        self.headers = headers if headers is not None else {}
        self.url = urlp
        self.client = ""
        self._inner_body = json_body 
        self.body = self.get_body


    async def get_json(self):
        return self._inner_json


    async def get_body(self):
        return self._inner_body



