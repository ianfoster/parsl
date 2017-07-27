
// WORKFLOW

import io;
import string;
import location;
import python;
pragma worktypedef controller;


@dispatch=CONTROLLER
(string output) python_persist_controller(string code, string expr) "turbine" "0.1.0"
[ "set <<output>> [ turbine::python 1 <<code>> <<expr>> ]" ];


@dispatch=WORKER
(string output) python_persist_worker(string code, string expr) "turbine" "0.1.0"
[ "set <<output>> [ turbine::python 1 <<code>> <<expr>> ]" ];


(string tasks) get_tasks()
{
    tasks = python_persist_controller("import swift_e",
                           "swift_e.get_tasks()");
}

(string result) make_queues(string jobs_q, string results_q)
{
    result = python_persist_controller("import swift_e",
                            "swift_e.make_queues(\"%s\", \"%s\")" % (jobs_q, results_q) );
                            //"test.test_parallel_for(100)");
}

(string result) task(string arguments)
{
    result = python_persist("import swift_e",
                            "repr(swift_e.task(\"%s\"))" % arguments);
}

(boolean result) put_results(string results)
{
    python_persist_controller("import swift_e",
                   "swift_e.put_results(\"%s\")" % results) =>
        result = true;
}

(boolean result) run_tasks(string taskstring)
{
    return_val = task(taskstring) =>
        put_results(return_val) =>
        result = true;
}


x = make_queues("tcp://127.0.0.1:5557", "tcp://127.0.0.1:5558") =>
  trace("Queue return : %s"% x) =>
  y = get_tasks() =>
  trace("Task get : %s" % y) =>
  loop();

loop()
{
    for (boolean b = true; b; b=c){

        printf("In loop");
        boolean c;
        tasks = get_tasks() ; //=> trace("tasks : %s" % tasks);
        if (tasks == "EMPTY") {
            printf("Empty....");
            c = true;
        }else{
            printf("Received : %s", tasks);
            if (tasks == "DONE") {
                printf("Done");
                c = false;
            }else{
                printf("Running task : %s", tasks);
                c = run_tasks(tasks);
            }
        }

        /*
        if (tasks == "DONE") {
            printf("Done");
            c = false;

        }else{
        }
        */
    }
}
