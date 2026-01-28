# the data transfer object for the actor.


from dataclasses import dataclass
from app.logging import gCon
from app.ap_api.AsyncRequest import AsyncGetReq
from app.api.AdelphosException import AdelphosException
from urllib.parse import urlparse
import json

table_name = "actor"

# the actor is NOT an adelphos object.


# this is the base class for the activity pub actors.
@dataclass
class ActorDto:

    actor_id: int = None

    server_fk: int = None

    #actor_uri: str = None
    #canonical_name: str = None 
    #inbox_uri: str = None

    user_path: str = None
    preferred_name: str = None
    inbox_path: str = None
    public_key: str = None

    # this is the user name imposed by the server (for example mastodon
    # imposes a long integer id)
    #user_server_name: str = None
    # this is the preferred name, like @<user>@<host>

    timestamp: str = None


# this is the class that holds the data for an actor and a server
# at the same time, it queries the actor_server view. 
@dataclass
class ActorServerDto:
    actor_id: int = None
    host_name: str = None

    user_path: str = None
    preferred_name: str = None
    inbox_path: str = None
    public_key: str = None
    timestamp: str = None



# this is the class that holds the logic to query and to
# instantiate actor DTOs
# This Dao does not derive from AdelphosObjectDao because
# the actors are not part of the adelphos federated DB
class ActorDao:


    # I can set here the context.
    def __init__(self, dao):
        self.dao = dao


    # gets from local database or queries the webfinger endpoint
    @staticmethod
    async def get_or_discover_actor(ctx, preferred_username, rem_instance):

        actor = ActorDto.get_from_canonical_name(ctx, preferred_username,
                                                 rem_instance)
        if (actor is not None):
            return actor

        return await ActorDto.find_remote_actor(ctx,
                        preferred_username, rem_instance)


    # this function will query a remote actor in Activity Pub; it is working
    # for a daemon too, which is only another actore.
    @staticmethod
    async def find_remote_actor(ctx, preferred_username, rem_instance):

        actor_query = f"https://{rem_instance}/.well-known/webfinger?\
resource=acct:{preferred_username}@{rem_instance}"

        actor_res = AsyncGetReq(actor_query)
        await ctx.app.async_req_wait(actor_res)

        if (actor_res.status_code != 200):
            raise AdelphosException(
                    f"remote instance not responding: {rem_instance}")

        actor_ob = json.loads(actor_res.text)

        subject = actor_ob['subject']
        if ( subject != f"acct:{preferred_username}@{rem_instance}"):
            raise AdelphosException(f"got {subject} instead!")

        actor = ActorDto()
        actor.actor_uri = actor_ob['links'][0]['href']
        
        # Now we do the request for the actor
        daemon_actor = AsyncGetReq(actor.actor_uri)
        await ctx.app.async_req_wait(daemon_actor)

        if (daemon_actor.status_code != 200):
            raise AdelphosException(
                f"remote instance misconfigured {actor.actor_uri}")

        actor_ob = json.loads(daemon_actor.text)

        # OK, we can now take the inbox and the public key.
        actor.inbox_uri = actor_ob['inbox']
        actor.public_key = actor_ob['publicKey']['publicKeyPem']
        actor.preferred_username = preferred_username 
        actor.canonical_name = f"@{preferred_username}@{rem_instance}"

        actor.id = actor.store(ctx)
        return actor


    @staticmethod
    def _base_get(ctx, fields_to_seek, values_to_seek):
        global table_name

        fields_to_ask = ('actor_id', 'actor_uri', 'canonical_name', 
                         'inbox_uri', 'public_key', 'timestamp')

        dto = ctx.app.dao.get_dto_ex(table_name, fields_to_ask, 
                                     fields_to_seek, 
                            values_to_seek, ActorDto)
        gCon.log(f"I have grabbed {dto} from db")
        return dto      


    # this function will fetch the public key of the actor
    async def create_from_uri(ctx, actor_uri, key_parsed):

        gCon.log(f"Create here a cached actor {actor_uri}")
        actor = ActorDto()
        actor.actor_uri = actor_uri

        res_key = AsyncGetReq(actor_uri)
        await ctx.app.async_req_wait(res_key)

        if (res_key.status_code != 200):
            gCon.log(f"Could not fetch the public key {res_key.status_code}")
            return False

        key_ob_text = res_key.text

        key_ob = json.loads(key_ob_text)

        gCon.log(f"this is the actor {key_ob}")

        pub_key_ob = key_ob['publicKey']

        pub_key_ob_id = pub_key_ob['id']
        actor.public_key = pub_key_ob['publicKeyPem']

        # are they the same?
        if (pub_key_ob_id != key_parsed.geturl()):
            raise AdelphosException(f"Error, got {pub_key_ob_id} key \
exp {actor_uri}")

        # is the owner?
        owner = pub_key_ob['owner'] 
        if (owner != actor_uri):
            gCon.log(f"This is bad {pub_key_ob}")
            gCon.log(f"Error, {owner} different from {actor_uri}")
            raise AdelphosException("Bad key")

        actor.inbox_uri = key_ob['inbox']
        preferred_username = key_ob['preferredUsername']
        gCon.log("I have set the canonical name")
        actor.canonical_name = f"@{preferred_username}@{key_parsed.hostname}"

        actor.actor_id = actor.store(ctx)

        return actor 


    # this function tries to get an actor from
    # the local db using the hostname and 
    def get_local_from_parsed_uri(self, ctx, key_parsed):
        # I have to query the view.
        gCon.log(f"this actor's Activity Pub host is {key_parsed.netloc}")
        gCon.log(f"his path is  is {key_parsed.path}")
        return None


    async def get_or_discover_from_pk_id(self, ctx, key_id_val):

        # OK, I have the public key identifier, now I have to decompose it
        # in host, path and fragment (the last one is usually removed)

        key_parsed = urlparse(key_id_val)

        parsed = key_parsed._replace(fragment = "")
        actor_uri = parsed.geturl()

        actor = self.get_local_from_parsed_uri(ctx, key_parsed)

        if (actor is None):
            actor = await ActorDto.create_from_uri(ctx, actor_uri, 
                                                   key_parsed)
        return actor


    @staticmethod
    def get_from_uri(ctx, actor_uri):

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

        newid = ctx.app.dao.insert_dto(ctx, table_name, fields_stored)

        gCon.log(f"stored {self.actor_uri} canonical {self.canonical_name}\
 his id {newid}")

        return newid


    def update(self, ctx):
        pass


    def delete(self, ctx):
        pass

