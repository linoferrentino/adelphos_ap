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
# This is the base class of all the world in Adelphos
# this is agnostic relative to the interface above (GUI or CLI)
# and the implementation below (which can be a DB or anything else)

# It contains only the logic of the fractal trust network

# no authorization or authentication is done here, the class
# assumes that these are handled at outer layers.

# usually the functions in this class return 0 on OK, -errno in case
# of error 

# in case a negative value is a valid answer the function will return None
# and the last error is set in the object.

# each action is part of a transaction.

from argon2 import PasswordHasher

from app.dao.AdelphosUri import uriparse_type, EAdelphosType
from app.core.LocalModel import LocalModel
from app.core.InstancesModel import InstancesModel

from app.logging import gCon

from app.federation.SocialListener import SocialListener


# Adelphos is the main object which orchestrates all the messages.
class Adelphos(SocialListener):


    def __init__(self, config, name, db, social):
        self.config = config
        self.name = name
        self.db = db
        self.social = social

        # this is the Local Model
        self.model = LocalModel(0, db)

        # I have a set of instances, myself and the allowed ones. 
        self.instances = InstancesModel()

        self.initialization()


    def initialization(self):

        # Now I have to discover the root actor.
        #flag = self.dao.created_schema_flag()
        ##del self._init_schema
        #if (flag == False):
        #    return

        self.create_myself_as_actor()

        # Now I want to create some other aliases, this MUST BE DONE before,
        # because the root actor might be internal.
        self.ap_mockup.create_test_users()

        # when I return from this function the test users are created, so
        # I can create the root.

        # we have to discover the root actor
        # in another task, because we might be the target!
        root_user = self.config['General']['root_user']
        #gCon.log(f"Creating root user {root_user} for {self.instance}")
        if (root_user != ':local:'):
            asyncio.create_task(self.create_root_actor(root_user))

        #gCon.rule(f"COMMIT OF INITIAL DB (minus the root actor) for {self.instance}")
        self.db.commit()


    async def new_post(self, post):
        pass


    # the aliases subsystem
    #def alias_ss(self):
    #    return self.alias_ss


    #def add_federated_adelphos(self, other_adelphos):
    #    pass



    #def create_alias_pass(self, actor_id, alias, password):

    #    alias_uri = uriparse_type(alias, EAdelphosType.ALIAS_TYPE)

    #    if (alias_uri.is_numeric == True):
    #        raise AdelphosException("Cannot create a numeric alias")

    #    #gCon.log(f"alias uri created {alias_uri}")

    #    family_dto = self.gateway.app.dao.family_dao.get_from_local_name(
    #            alias_uri.family)

    #    if (family_dto is not None):
    #        raise AdelphosException(
#f"fa#mily {alias_uri.family} is already existing in this instance")

    #    ph = PasswordHasher()
    #    pass_hashed = ph.hash(password)

    #    # we are creating here an alias in instance zero.
    #    self.gateway.app.dao.alias_dao.create_alias_impl(
    #        actor_id, alias_uri.family, 0, alias_uri.name, pass_hashed)


    #@commit_if_ok
    #def alias_uri_create(self, actor_id, alias_uri, password):

    #    alias_uri = uriparse_type(alias, EAdelphosType.ALIAS_TYPE)

    #    if (alias_uri.is_numeric == True):
    #        raise AdelphosException("Cannot create a numeric alias")

    #    self._alias_create_impl(actor_id, alias_uri.name,
    #        alias_uri.family, password)



    #def get_items(self, alias_id, my_equity):
    #    pass
