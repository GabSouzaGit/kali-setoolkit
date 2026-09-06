import time

def benchmark(callback_wrapper):
    start = time.perf_counter()
    callback_wrapper()
    end = time.perf_counter()

    return end - start
