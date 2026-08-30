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


import math


def abs_to_db(val):
    return 10.0 * math.log10(val)


def db_to_abs(valdb):
    return math.pow(10.0, valdb / 10.0)

