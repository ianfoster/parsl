# Untested

from libsubmit.providers import CobaltProvider
from libsubmit.launchers import SingleNodeLauncher

from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.ipp_controller import Controller
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
            label='cooley_local_single_node',
            provider=CobaltProvider(
                launcher=SingleNodeLauncher(),
                nodes_per_block=1,
                tasks_per_node=1,
                init_blocks=1,
                max_blocks=1,
                walltime="00:05:00",
                overrides=user_opts['cooley']['overrides'],
                queue='debug',
                account=user_opts['cooley']['account']
            ),
            controller=Controller(public_ip="10.230.100.210")
        )

    ],
    run_dir=get_rundir(),
)
