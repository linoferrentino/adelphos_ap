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

# a Line is between two aliases,
# adelphos is a system of people.
# 
# we recognize abstract groups, but they are only used
# as ways to save trust.

# in a group the trust is conserved.

# We do not have a level explicit here; the level is implicit
# by the topology of the network.

# a line between two aliases is at least at level 1,
# but it can also be at level 2, 3, n... if the aliases
# who agree to put a bridge are on different group.

# remember: adelphos is at its core a trust amplifier.

class LineDto(FdObjectDto):

    alias_1_fk: int

    alias_2_fk: int

    # Every line is associated to a task, the judge is a person who both
    # people agree to be their judge in case of controversy.
    judge_fk: int


