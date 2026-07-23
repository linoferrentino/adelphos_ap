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


def abs_to_db(val_abs):
    return 10.0 * math.log10(val_abs)


def db_to_abs(val_db):
    return math.pow(10.0, val_db / 10.0)
