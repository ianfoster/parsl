alias python='python3'
TCL_PATH=/home/wozniak/Public/sfw/login/gcc/tcl-8.6.1-global/bin
STC_PATH=/home/wozniak/Public/sfw/login/gcc/swift-t-py-3.6.1/stc/bin
TURBINE_PATH=/home/wozniak/Public/sfw/login/gcc/swift-t-py-3.6.1/turbine/bin
PY_PATH=/home/wozniak/Public/sfw/Python-3.6.1/bin
export PATH=$TCL_PATH:$STC_PATH:$TURBINE_PATH:$PY_PATH:$PATH
export  LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/wozniak/Public/sfw/Python-3.6.1/lib
export PYTHONPATH=/scratch/midway/yadunand/swift-e-lab:/scratch/midway/yadunand/swift-e-lab/sti/1/libs/lib/python3.6/site-packages/:/scratch/midway/yadunand/swift-e-lab/sti/1/libs/lib/python3.6/::/scratch/midway/yadunand/swift-e-lab/sti/1/libs:/home/wozniak/Public/sfw/Python-3.6.1/lib:$PYTHONPATH

export TURBINE_LOG=1
export TURBINE_CONTROLLER_WORKERS=1
