"""
================== Block
| ++++++++++++++ | Node
| |            | |
| |    Task    | |             . . .
| |            | |
| ++++++++++++++ |
==================
"""
from libsubmit.channels import LocalChannel
from libsubmit.providers import GridEngineProvider
from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.tests.utils import get_rundir

# If you are a developer running tests, make sure to update parsl/tests/configs/user_opts.py
# If you are a user copying-and-pasting this as an example, make sure to either
#       1) create a local `user_opts.py`, or
#       2) delete the user_opts import below and replace all appearances of `user_opts` with the literal value
#          (i.e., user_opts['swan']['username'] -> 'your_username')
from .user_opts import user_opts

config = Config(
    executors=[
        IPyParallelExecutor(
            label='cc_in2p3_local_single_node',
            provider=GridEngineProvider(
                channel=LocalChannel(),
                nodes_per_block=1,
                tasks_per_node=1,
                init_blocks=1,
                max_blocks=1,
                walltime="00:20:00",
                overrides=user_opts['cc_in2p3']['overrides'],
            ),
            engine_debug_level='DEBUG',
        )

    ],
    run_dir=get_rundir()
)
