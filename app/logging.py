from rich.console import Console

import sys

# I create the global console object.

gCon = Console()


def good_bye(msg):
    gCon.log("Normal exit: " +  msg)
    sys.exit(0)

def exit_err(msg):
    gCon.log("Exit error: " +  msg)
    sys.exit(1)


