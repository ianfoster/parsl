import argparse

import parsl
from parsl.app.app import App
from parsl.tests.configs.local_threads import config

parsl.clear()
dfk = parsl.load(config)


def test_python_memoization(n=2):
    """Testing python memoization when func bodies differ
    This is the canonical use case.
    """
    @App('python', dfk)
    def random_uuid(x, cache=True):
        import uuid
        return str(uuid.uuid4())

    x = random_uuid(0)
    print(x.result())

    @App('python', dfk)
    def random_uuid(x, cache=True):
        import uuid
        print("hi")
        return str(uuid.uuid4())

    y = random_uuid(0)
    assert x.result() != y.result(), "Memoized results were not used"


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--count", default="10",
                        help="Count of apps to launch")
    parser.add_argument("-d", "--debug", action='store_true',
                        help="Count of apps to launch")
    args = parser.parse_args()

    if args.debug:
        parsl.set_stream_logger()

    x = test_python_memoization(n=4)
