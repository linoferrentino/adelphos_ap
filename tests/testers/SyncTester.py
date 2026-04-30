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


from urllib.parse import urlsplit


class SyncTester:

    def __init__(self, app):
        self.app = app


    def _check_path(self, path):

        urls = urlsplit(path)
        if len(urls.scheme) != 0:
            raise Exception(f"I did not expect a scheme {urls.scheme}")
        if len(urls.netloc) != 0:
            raise Exception("I did not expect a location")
        return urls


    def post(self, path, json):
        if (isinstance(path, str)):
            urlparse = self._check_path(path)
        elif (isinstance(path, int)):
            urlparse = path
        else:
            raise Exception(f"type {path} not expected got {type(path)}")
        return self.app.in_post_json(urlparse, json)
        

    def get(self, path):
        pass

