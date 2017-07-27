Swift-T Interface New
=====================

This is Parsl over Swift-T prototype. Parsl and Swift-T run on individual processes with all IPC going
over 0mq. The 0mq code is `zmq_pipe.py`.

Results
-------

Performance measurements done on swift.rcc.uchicago.edu. Tests were done on a single node with Intel(R) Xeon(R) CPU X5675 @ 3.07GHz.
The swift-t executor was run with 6 MPI ranks, with 4 worker ranks and 1 controller rank.

+------------+------------+--------------------+
| Task Count | TTC(s)     | Task Rate(Tasks/s) |
+============+============+====================+
|  10        |    0.875   |       11.428       |
+------------+------------+--------------------+
|  100       |    0.981   |      101.936       |
+------------+------------+--------------------+
|  1000      |    1.570   |      636.942       |
+------------+------------+--------------------+
|  10000     |    8.67    |     1153.402       |
+------------+------------+--------------------+
|  100000    |   78.886   |     1267.652       |
+------------+------------+--------------------+
|  1000000   |  771.639   |     1295.942       |
+------------+------------+--------------------+

How to run
----------

The setup_env.sh brings the right codes into the run environment on midway:

>>> . setup_env.sh

This setup script also sets up the following env variables which are picked up by Swift-t:

>>> export TURBINE_LOG=1
>>> export TURBINE_CONTROLLER_WORKERS=1
>>> export TURBINE_SLAVES_WORKERS=4

Run the swift-t in executor flow

>>> swift-t -l -n 6 executor.swift

Then we start the python code, that launches tasks

>>> python3 test.py




Swift/T Interface 1 OLD
===================

This workflow demonstrates the simplest way to let Python control a Swift/T workflow.

**Source:** https://github.com/swift-lang/swift-e-lab ``sti/1`` (branch ``rework-executors``)

Files
-----

workflow.swift
  This is the main workflow.  Run with:

::

  $ export PYTHONPATH=$PWD
  $ swift-t workflow.swift

swift_e.py
  This is a set of Python functions called by Swift/T.  There are Swift/T functions with matching names.

Functions
---------

The Python & Swift/T functions are:

get_tasks()
  Gets a set of tasks from Python.

task()
  Computes on a task in Python (does a ``sum()``) with added delay.

put_results()
  Posts the sums back to Python.

TODO
----

The script runs forever.  We could make it stop by having Python return ``"DONE"``.

Transcript
----------

Example usage:

::

  $ swift-t -l -n 5 workflow.swift
  [0] python: new tasks: [6, 1, 6];[5, 1, 6];[4, 0, 4]
  [1] python: compute:   [5, 1, 6]
  [2] python: compute:   [6, 1, 6]
  [3] python: compute:   [4, 0, 4]
  [0] python: results:   13;12;8
  [1] python: new tasks: [9, 0, 3];[7, 7, 5];[1, 5, 5]
  [0] python: compute:   [9, 0, 3]
  [3] python: compute:   [7, 7, 5]
  [2] python: compute:   [1, 5, 5]
  [1] python: results:   12;19;11
  ...

As shown by the MPI rank prefixes, the Python compute tasks run on different ranks.
