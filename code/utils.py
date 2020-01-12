import time
import os


def swap(file_name, destroy):
    data = []
    for line in open(file_name, 'r').readlines():
        data.append(line.replace('\n', ''))
    if destroy:
        os.remove(file_name)
    return data


def fcn_timer(func, args):
    tic = time.time()
    result = func(args)
    return result, time.time() - tic

