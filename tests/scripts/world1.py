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
        -  name: ad1
           host: www.ad1.com
           root: ad1root
           password: ad1pass
           accepts:
             - ad2
             - ad3
        -  name: ad2
           host: www.ad2.com
           root: ad2root
           password: ad2pass
           accepts:
             - ad1 
             - ad3
        -  name: ad3
           host: www.ad3.com
           root: ad3root
           password: ad3pass
           accepts:
             - ad2
             - ad1

"""
