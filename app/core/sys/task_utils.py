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


from app.logging import gCon

def add_task_to_alias(kernel, alias, task):

    gCon.log(f"[red]Adding {task} to {alias}[/red]")
