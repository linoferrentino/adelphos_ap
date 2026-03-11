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
# this is the Mockup used to store the fake users in this Adelphos instance
# (useful for testing and integrating)

from app.logging import gCon
from app.dao.ApActorDto import create_ap_actor
from app.consts import API_POINT

# then there is the Mockup user
class MockupUser:

    def post_message():
        pass

    def clear_messages():
        pass

    def get_messages():
        pass



class ActivityPubMockup:


    def __init__(self, app):
        self.app = app
        self.users = {}


    # queries the db in order to get the answer
    def ap_user_exists(self, activity_pub_user):
        # OK, I have to query the db, the server MUST be zero
        ap_actor = self.app.dao.ap_actor_dao.get_from_preferred_username(0, activity_pub_user)
        gCon.log(f"Obtained actor {ap_actor}")
        if (ap_actor is None):
            return False
        return True


    def ap_user_info(self, activity_pub_user):
        ap_actor = self.app.dao.ap_actor_dao.get_from_preferred_username(0, activity_pub_user)
        if (ap_actor is None):
            return None
        return ('actor', activity_pub_user, f"Mockup actor for instance {self.app.instance}")


    def create_test_users(self):

        if (self.app.config.get('demo_users') is None):
            gCon.log("no demo users defined")
            return

        demo_users = self.app.config['demo_users']
        for demo_user in demo_users:
            # by definition the users belong to my server.
            # they are ``embedded'' in this instance, so they belong to
            # ap_server 'zero'
            gCon.log(f"I want to create {demo_user}")
            # first of all I have to create the actor, the server is our server
            # and his/her key is the application's key.
            actor_id = self.create_app_actor(demo_user['name'])
            # Now I will create the alias.
            gCon.log(f"The new actor has the id {actor_id}")
            # I have to create the alias, using the alias and the password
            self.app.ap_gateway.ap_alias_api.create_alias_pass(
                    actor_id, demo_user['alias'], demo_user['password'])


    # creates an actor which sits in the instance (only useful for testing)
    def create_app_actor(self, actor_name, forced_id = None):
        user_path = API_POINT + f"/users/{actor_name}"
        user_inbox = user_path + "/inbox"
        # the server is hard coded to zero, we are in the app realm
        myself_actor = create_ap_actor(0, user_path, user_inbox,
                                       actor_name, self.app.public_key)
        if (forced_id is not None):
            myself_actor.actor_id = 0
            actor_id = self.app.dao.ap_actor_dao.store_full_no_ts(myself_actor)
        else:
            actor_id = self.app.dao.ap_actor_dao.store(myself_actor)

        gCon.log(f"Created actor {actor_name} with id {actor_id}")
        return actor_id


