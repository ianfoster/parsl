''' Testing bash apps
'''
import parsl
from parsl import *
#from parsl.executors.swift_e import *
from swift_e import *
import os
import time
import shutil
import argparse

#parsl.set_stream_logger()
#workers = ThreadPoolExecutor(max_workers=4)
workers = TurbineExecutor(jobs_q_url="tcp://127.0.0.1:5557",
                          results_q_url="tcp://127.0.0.1:5558")

#dfk = DataFlowKernel(workers)

@App('python', workers)
def double(x):
    return x*2


def foo():
    print ("Hello world")
    return "Hello"

def test_parallel_for(count):
    '''
    This function has to return a string
    '''

    '''
    print("Parallel For of width ", count)

    x = {}
    for i in range(0, count):
        x[i] = double(i)

    '''
    #return x
    return "FOOOOOOoo"

def parallel_for(count):
    '''
    This function has to return a string
    '''

    print("Parallel For of width ", count)
    return [double(i) for i in range(0, count)]



if __name__ == '__main__' :

    parser   = argparse.ArgumentParser()
    parser.add_argument("-c", "--count", default="10", help="Count of apps to launch")
    parser.add_argument("-d", "--debug", action='store_true', help="Count of apps to launch")
    args   = parser.parse_args()

    if args.debug:
        parsl.set_stream_logger()

    x = parallel_for(int(args.count))

    #print([i.done() for i in x])

    final = [i.result() for i in x]
    print(final)

    assert final == [i*2 for i in range(0, int(args.count)) ]

    #raise_error(0)

