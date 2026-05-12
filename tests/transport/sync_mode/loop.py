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
    
    loop.set_debug(True)
    loop_started.set()
    loop.run_forever()


def _create_loop():
    global run_loop_th
    run_loop_th = threading.Thread(target = in_saecula_saeculorum)
    run_loop_th.start()


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


def run_coro_in_loop(endpoint, request, wait = True):

    res = run_coro_in_loop_generator(endpoint, request, wait)
    res_task = next(res)
    return res_task


def run_coro_in_loop_generator(endpoint, request, wait = True):

    if threading.current_thread() == run_loop_th:
        task = asyncio.create_task(endpoint(request))
        yield task
        
    future = asyncio.run_coroutine_threadsafe(endpoint(request), get_loop())
    if wait == True:
        res = future.result()
        if isinstance(res, asyncio.Task) == True:
            res = res.result()
        yield res
    else:
        yield



