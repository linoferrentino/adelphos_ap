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


from enum import IntEnum


class ECoreErrno(IntEnum):
    DONE_OK = 0
    EDUPLICATED_FAMILY = 1
    EINVALID_ALIAS_SYNTAX = 3
    EINVALID_USER_OR_PASSWORD = 4
    EINVALID_TRUST = 5
    EINVITE_ALREADY_PRESENT = 6
    ECANNOT_FIND_INVITE = 7
    EWRONG_INVITE_CODE = 8
    EWRONG_USER_HANDLE = 9
    EINVALID_CHAIN = 10
    EFAMILY_NOT_FOUND = 11
    EDENIED = 12
    EEQUITY_OVERFLOW = 13
    EUPLEVEL_NOT_FOUND = 14
    EDIFFERENT_LEVELS = 15
    EALREADY_ASSOCIATED = 16
    EINVALID_AD_INDEX = 17
    ECANNOT_BUY_IN_YOUR_FAMILY = 18
    ENO_SUCH_OBJECT = 19
    EINSUFFICIENT_TRUST_IN_ADELPHOS = 20
    EINSUFFICIENT_TRUST_FROM_ADELPHOS = 21

    
    EFDB = 9998
    ESYS = 9999


