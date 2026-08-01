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


import secrets


class WrapInt:

    def __init__(self, nbits = 31, init_int = None):
        if ((nbits < 2) or (nbits > 31)):
            raise Exception(f"nbits out of range {nbits}")

        self.max_val = (pow(2, nbits) - 1)

        if init_int is None:
            self.val = secrets.randbits(nbits)
            return

        initval = int(init_int)
        if ((initval < 0) or (initval > self.max_val)):
            raise Exception(f"initval {initval} out of range [0..{self.val}]")
        self.val = initval


    def get_and_inc(self):
        val = self.val
        self.val = self.inc_and_get_val(val)

        return val


    def inc_and_get_val(self, val):
        if val == self.max_val:
            val = 0
        else:
            val += 1
        return val


W32 = WrapInt(nbits = 31)
