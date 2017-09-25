#!/usr/bin/env python3.5
import sys

import parsl
from parsl import *

parsl.set_stream_logger()

from parsl.executors.swift_t import *


def foo(x, y):
    z = x*y
    #print("Print hi ", z)
    return x*y

def slow_foo(x, y):
    import time
    time.sleep(x)
    return x*y

def bad_foo(x, y):
    time.sleep(x)
    return x*y


def test_simple():
    print("Start")
    tex = TurbineExecutor()
    x = tex.submit(foo, 5, 10)
    print("Got : ", x)
    print("X result : ", x.result())
    assert x.result() == 50 , "X != 50"
    print("done")

def test_except():
    print("Start")
    tex = TurbineExecutor()
    x = tex.submit(bad_foo, 5, 10)
    print("Got : ", x)

    print("X exception : ", x.exception())
    print("X result : ", x.result())

    print("done")


def test_loop(count):
    print("Start")
    tex = TurbineExecutor()
    fus = {}
    for i in range(count):
        fus[i] = tex.submit(foo, i, 10)

    for i in fus:
        print (i, fus[i])
        print("result : ", fus[i].result())

    print("done")



if __name__ == "__main__":


    #test_simple()
    test_loop(100)
    #test_except()
    exit(0)
    futs = {}
    for i in range(0,3):
        futs[i] = tex.submit(foo, 3, 10)


    #x.result(timeout=10)
    for x in range(0,3):
        print(futs)
        time.sleep(4)

    print("Done")

