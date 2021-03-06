import pytest

from parsl.app.app import App
from parsl.dataflow.dflow import DataFlowKernel


def run_checkpointed(checkpoints):
    # set_stream_logger()
    from parsl.tests.configs.local_threads_checkpoint_task_exit import config
    config.checkpoint_files = checkpoints
    dfk = DataFlowKernel(config=config)

    @App('python', dfk, cache=True)
    def cached_rand(x):
        import random
        return random.randint(0, 10000)

    items = []
    for i in range(0, 5):
        x = cached_rand(i)
        items.append(x)

    dfk.cleanup()
    return [i.result() for i in items], dfk.run_dir


def run_race(sleep_dur):

    from parsl.tests.configs.local_threads_checkpoint_dfk_exit import config
    dfk = DataFlowKernel(config=config)

    @App('python', dfk, cache=True)
    def cached_rand(x, sleep_dur=0):
        import random
        import time
        time.sleep(sleep_dur)
        return random.randint(0, 10000)

    items = []
    for i in range(0, 5):
        x = cached_rand(i, sleep_dur=sleep_dur)
        items.append(x)

    dfk.cleanup()
    return [i.result for i in items]


@pytest.mark.local
@pytest.mark.forked
def test_regress_234():
    """Test task_exit checkpointing with fast tasks"""
    run_race(0)


@pytest.mark.local
@pytest.mark.forked
def test_slower_apps():
    """Test task_exit tests with slow apps"""
    run_race(0.5)


@pytest.mark.local
@pytest.mark.forked
def test_checkpoint_availability():
    import os

    original, run_dir = run_checkpointed([])
    last_checkpoint = os.path.join(run_dir, 'checkpoint')
    print(last_checkpoint)
    cached, _ = run_checkpointed([last_checkpoint])

    print(cached)
    print(original)

    assert cached == original, "All tasks were not cached"


if __name__ == "__main__":

    test_checkpoint_availability()
    # test_regress_234()
    # test_slower_apps()
