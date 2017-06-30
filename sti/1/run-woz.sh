#!/bin/sh
set -eu

# RUN-WOZ
# This is just a convenience script for Wozniak

# PATH=$HOME/sfw/swift-t/stc/bin:$HOME/sfw/Python-2.7.10/bin:$PATH
# export PYTHONPATH=$HOME/sfw/Python-2.7.10/lib/python2.7:$PWD

# Midway:
SFW=$HOME/Public/sfw
PY=$SFW/Python-3.6.1
SWIFT_T=$SFW/login/gcc/swift-t-py-3.6.1
PATH=$PY/bin:$PATH
PATH=$SWIFT_T/stc/bin:$PATH
export PYTHONPATH=$PY/lib/python3.6/site-packages

source ./setup_env.sh

which swift-t python3

swift-t -l -n 6 workflow.swift &
sleep 5
python3 test.py

wait

