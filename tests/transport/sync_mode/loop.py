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

import threading
from app.logging import gCon
import time
import asyncio

loop = None
run_loop_th = None
loop_lock = threading.Lock()
loop_started = threading.Event()


def in_saecula_saeculorum():
    global loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    loop_started.set()
    gCon.log("run forever start")
    loop.run_forever()
    gCon.log("run forever stop")


def _create_loop():
    global run_loop_th
    gCon.log(f"Will start the loop! {threading.current_thread()}")
    run_loop_th = threading.Thread(target = in_saecula_saeculorum)
    run_loop_th.start()


def get_loop():
    global loop
    try:
        loop_lock.acquire()
        while True:
            if loop is not None:
                gCon.log(f"loop is not none, I return it")
                return loop
            _create_loop()
            loop_started.wait()
            gCon.log(f"Event signaled, now loop is {loop}")
            loop_started.clear()
    finally:
        loop_lock.release()

    
def stop_loop():
    global loop

    try:
        loop_lock.acquire()
        if loop is None:
            gCon.log(f"nothing to stop!")
            return
        gCon.log("loop will be stopped!")
        loop.call_soon_threadsafe(loop.stop)
        loop = None
        run_loop_th.join()
        gCon.log(f"loop is stopped! loop is {loop}")
    finally:
        loop_lock.release()


def run_coro_in_loop(endpoint, request):

    if threading.current_thread() == run_loop_th:
        gCon.log("I am in the loop thread.")
        result = get_loop().run_until_complete(endpoint(request))
        #task = asyncio.create_task(endpoint(request))
        #yield
        gCon.log(f"result is {result}")
        return result
        #result = await task
        #return result

    gCon.log("I am in the main thread.")
    future = asyncio.run_coroutine_threadsafe(endpoint(request), get_loop())
    res = future.result()
    return res



