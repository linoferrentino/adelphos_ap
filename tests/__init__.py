
import multiprocessing as mp
import time


# for some reasons it seems that it does not get the method right
method = mp.get_start_method()
already_done = False
#print(f"============================== method {method} {already_done} {id(already_done)}")
if method == 'fork':
    if already_done == True:
        print("already done!")
    else:
        print("xxxxxxxxxxxxxxxxxxxxxxxxx I set here!")
        already_done = True
        #mp.set_start_method('spawn', force = True)
        mp.set_start_method('spawn', force = True)
        #time.sleep(1)
