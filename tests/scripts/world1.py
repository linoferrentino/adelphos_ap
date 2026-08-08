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


world_1_yaml = """

    instances:
        - www.ad1.com:
           root: ad1root
           password: ad1pass
           accepts:
             - www.ad2.com
             - www.ad3.com
        - www.ad2.com:
           root: ad2root
           password: ad2pass
           accepts:
             - www.ad1.com
             - www.ad3.com
        - www.ad3.com:
           root: ad3root
           password: ad3pass
           accepts:
             - www.ad2.com
             - www.ad1.com

"""
