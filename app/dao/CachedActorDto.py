# the data transfer for the cached actor.


from dataclasses import dataclass
from app.logging import gCon

table_name = "cached_actor"

@dataclass
class CachedActorDto:

    actor_id: int = 0

    # these are fields which are stored in db.
    preferred_username: str = None
    hostname: str = None
    actor_uri: str = None
    inbox_uri: str = None
    public_key: str = None

    date_created: str = None


    @staticmethod
    def _base_get(ctx, fields_to_seek, values_to_seek):
        global table_name

        fields_to_ask = ('actor_id', 'preferred_username', 'hostname', 
                         'actor_uri', 'inbox_uri', 
                         'public_key', 'date_created')

        dto = ctx.app.dao.get_dto_ex(table_name, fields_to_ask, 
                                     fields_to_seek, 
                            values_to_seek, CachedActorDto)
        return dto      


    @staticmethod
    def get_from_name(ctx, actor_uri):

        field_to_seek = ('actor_uri',)
        value_to_seek = (actor_uri ,)

        return CachedActorDto._base_get(ctx, field_to_seek, value_to_seek)


    @staticmethod
    def get_from_fediverse_id(ctx, preferred_username, hostname):
        fields_to_seek = ('preferred_username', 'hostname')
        values_to_seek = (preferred_username, hostname)

        return CachedActorDto._base_get(ctx, fields_to_seek, values_to_seek)


    # this is used by the query that asks for the actor.
    @staticmethod
    def get_from_hostname(ctx, hostname):
        
        field_to_seek = ('hostname',)
        value_to_seek = (hostname, )

        return CachedActorDto._base_get(ctx, field_to_seek, value_to_seek)


    def store(self, ctx):

        global table_name

        fields_stored = {
                         'preferred_username': self.preferred_username,
                         'hostname': self.hostname,
                         'actor_uri': self.actor_uri,
                         'inbox_uri': self.inbox_uri,
                         'public_key': self.public_key,
                         }

        new_id = ctx.app.dao.insert_dto(ctx, table_name, fields_stored)

        gCon.log(f"Created new cached actor with id {new_id}")

        self.actor_id = new_id


    def update(self, ctx):
        pass


    def delete(self, ctx):
        pass

