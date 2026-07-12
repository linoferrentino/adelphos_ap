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

import re


class AdelphosBaseException(Exception):

    def __init__(self, realm, errno, detail = None):
        self.realm = realm
        self._errno = errno
        self.detail = detail


    @property
    def out_str(self):
        out_str = f"Adelphos {self.realm} error #{self._errno}#"
        if self.detail is not None:
            out_str += f">: {self.detail}"
        return out_str


    @staticmethod
    def parse_exc_str(err_str):
        re_match = re.search(rf"#(\d*)#", err_str)
        if re_match is None:
            return -1
        return int(re_match.group(1))


    @property
    def errno(self):
        return int(self._errno)


    @staticmethod
    def parse_detail(err_str):
        re_match = re.search(rf">: (.*)$", err_str)
        if re_match is None:
            return -1
        return re_match.group(1)


class AdelphosCoreException(AdelphosBaseException):

    def __init__(self, ad_errno, msg = None):
        super().__init__("core", ad_errno, msg)


