import time

def get_UTC_timestamp():
    t=time.time()
    stamp=int(round(t*1000))
    print stamp
    return stamp