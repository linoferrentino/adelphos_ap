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


import threading
from app.logging import gCon
import time
import asyncio

loop = None
run_loop_th = None
loop_lock = threading.Lock()
loop_started = threading.Event()


def my_handler(loop, context):
    gCon.log(f"Exception in loop! {context}")


class GlobalLoopPolicy(asyncio.DefaultEventLoopPolicy):


    def get_event_loop(self):

        global loop
        if loop is not None:
            gCon.log(f"returning the global loop {loop}")
            return loop

        gCon.log(f"get_event_loop called in policy")
        try:
            loop = super().get_event_loop()
        except RuntimeError:

            loop = asyncio.new_event_loop()
            gCon.log(f"There was not a loop, created {id(loop)}")
            asyncio.set_event_loop(loop)
            #loop = asyncio.get_running_loop()
            gCon.log(f"the loop in async io is {id(loop)}")
     
        loop.set_debug(True)
        loop.set_exception_handler(my_handler)
        gCon.log(f"get_event_loop called in policy returns {loop}")
        return loop


def in_saecula_saeculorum():
    global loop

    policy = asyncio.get_event_loop_policy()
    gCon.log(f"policy is {policy}")
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        gCon.log(f"There was not a loop, created {id(loop)}")
        asyncio.set_event_loop(loop)
        #loop = asyncio.get_running_loop()
        gCon.log(f"the loop in async io is {id(loop)}")
    
    #loop.set_debug(True)
    gCon.log(f"XXXXXXXXXXXXXXXX 1")
    loop_started.set()
    gCon.log(f"XXXXXXXXXXXXXXXX 2")
    #loop.set_exception_handler(my_handler)
    gCon.log(f"XXXXXXXXXXXXXXXX 3")
    gCon.log(f"XXXXXXXXXXXXXXXX created a loop {id(loop)} RUN NOW!")
    loop.run_forever()
    gCon.log(f"XXXXXXXXXXXXXXXX 4")



#def in_saecula_saeculorum():
#    global loop
#
#    policy = asyncio.get_event_loop_policy()
#    gCon.log(f"policy is {policy}")
#    try:
#        loop = asyncio.get_event_loop()
#    except RuntimeError:
#        loop = asyncio.new_event_loop()
#        gCon.log(f"There was not a loop, created {id(loop)}")
#        asyncio.set_event_loop(loop)
#        loop = asyncio.get_running_loop()
#        gCon.log(f"the loop in async io is {id(loop)}")
#    
#    loop.set_debug(True)
#    gCon.log(f"XXXXXXXXXXXXXXXX 1")
#    loop_started.set()
#    gCon.log(f"XXXXXXXXXXXXXXXX 2")
#    loop.set_exception_handler(my_handler)
#    gCon.log(f"XXXXXXXXXXXXXXXX 3")
#    gCon.log(f"XXXXXXXXXXXXXXXX created a loop {id(loop)}")
#    loop.run_forever()
#    gCon.log(f"XXXXXXXXXXXXXXXX 4")


def _create_loop():
    global run_loop_th

    asyncio.set_event_loop_policy(GlobalLoopPolicy())

    run_loop_th = threading.Thread(target = in_saecula_saeculorum)
    run_loop_th.daemon = True
    run_loop_th.start()
    gCon.log(f"created a loop in thread {run_loop_th.native_id}")


def get_loop():
    global loop
    try:
        loop_lock.acquire()
        while True:
            if loop is not None:
                return loop
            _create_loop()
            loop_started.wait()
            loop_started.clear()
    finally:
        loop_lock.release()

    
def stop_loop():
    global loop

    try:
        loop_lock.acquire()
        if loop is None:
            return
        loop.call_soon_threadsafe(loop.stop)
        loop = None
        run_loop_th.join()
    finally:
        loop_lock.release()


def run_coro_in_loop(endpoint, pars, *, wait = True):

    if threading.current_thread() == run_loop_th:
        task = asyncio.create_task(endpoint(*pars))
        return task

    future = asyncio.run_coroutine_threadsafe(endpoint(*pars), get_loop())
    if wait == False:
        return

    res = future.result()
    if isinstance(res, asyncio.Task) == True:
        res = res.result()
    return res


def is_in_loop():
    if threading.current_thread() == run_loop_th:
        return True
    return False



