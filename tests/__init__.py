
import multiprocessing as mp

method = mp.get_start_method()
if method == 'fork':
    mp.set_start_method('spawn', force = True)
