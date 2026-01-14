# the data transfer object for the actor.


from dataclasses import dataclass
from app.logging import gCon

table_name = "actor"

@dataclass
class ActorDto:

    actor_uri: str = None

    # these are fields which are stored in db.
    canonical_name: str = None 
    inbox_uri: str = None
    public_key: str = None

    # this field is computed by the Db, it is not part of the schema, it is
    # useful to prune old records.
    timestamp: str = None


    @staticmethod
    def _base_get(ctx, fields_to_seek, values_to_seek):
        global table_name

        fields_to_ask = ('actor_uri', 'canonical_name', 
                         'inbox_uri', 'public_key', 'timestamp')

        dto = ctx.app.dao.get_dto_ex(table_name, fields_to_ask, 
                                     fields_to_seek, 
                            values_to_seek, ActorDto)
        return dto      


    @staticmethod
    def get_from_name(ctx, actor_uri):

        field_to_seek = ('actor_uri',)
        value_to_seek = (actor_uri ,)

        return ActorDto._base_get(ctx, field_to_seek, value_to_seek)


    @staticmethod
    def get_from_canonical_name(ctx, preferred_username, hostname):
        canonical_name = f"@{preferred_username}@{hostname}"
        fields_to_seek = ('canonical_name', )
        values_to_seek = (canonical_name, )

        return ActorDto._base_get(ctx, fields_to_seek, values_to_seek)


    def store(self, ctx):

        global table_name

        fields_stored = {
                         'actor_uri': self.actor_uri,
                         'canonical_name': self.canonical_name,
                         'inbox_uri': self.inbox_uri,
                         'public_key': self.public_key,
                         }

        ctx.app.dao.insert_dto(ctx, table_name, fields_stored)

        gCon.log(f"Created new cached actor with id {self.actor_uri}")


    def update(self, ctx):
        pass


    def delete(self, ctx):
        pass

