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
from app.exc.AdelphosException import AdelphosException
from starlette.exceptions import HTTPException


class AbstractTransport(ABC):


    @abstractmethod
    async def post_json(self, url, json):
        pass


    @abstractmethod
    async def get_json(self, url):
        pass


    async def get_json_safe(self, url, errno):
        try:
            val = await self.get_json(url)
            return val
        except HTTPException as exc:
            raise AdelphosException(errno)


    @abstractmethod
    def in_get_json(self, urlp):
        pass


