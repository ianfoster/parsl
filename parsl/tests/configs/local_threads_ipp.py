"""The following config uses threads say for local lightweight apps and IPP workers for
heavy weight applications.

The app decorator has a parameter `executors=[<list of executors>]` to specify the executor to which
apps should be directed.
"""
from libsubmit.providers import LocalProvider
from parsl.config import Config
from parsl.executors.ipp import IPyParallelExecutor
from parsl.executors.threads import ThreadPoolExecutor
from parsl.tests.utils import get_rundir

config = Config(
    executors=[
        ThreadPoolExecutor(max_threads=4, label='local_threads'),
        IPyParallelExecutor(
            label='local_ipp',
            provider=LocalProvider(
                walltime="00:05:00",
                nodes_per_block=1,
                tasks_per_node=1,
                init_blocks=4
            )
        )
    ],
    run_dir=get_rundir()
)
