
// WORKFLOW

//import python;
import io;
import string;
import python;
//import location;

pragma worktypedef slaves;


(string output) python_r0(string code, string expr) "turbine" "0.1.0"
[ "set <<output>> [ turbine::python 1 <<code>> <<expr>> ]" ];

/*
@dispatch=slaves
(string output) python_persist(string code, string expr) "turbine" "0.1.0"
[ "set <<output>> [ turbine::python 1 <<code>> <<expr>> ]" ];
*/

/*
(string output) python_r0_worker(string code, string expr) "turbine" "0.1.0"
[ "set <<output>> [ turbine::python 1 <<code>> <<expr>> ]" ];

@dispatch=CONTROL
(string output) python_r0_server(string code, string expr) "turbine" "0.1.0"
[ "set <<output>> [ turbine::python 1 <<code>> <<expr>> ]" ];
*/

(string result) task(string arguments)
{
    result = python_r0("import swift_e",
                       "repr(swift_e.task(\"%s\"))" % arguments);
}

(boolean result) run_tasks(string taskstring)
{

    return_val = task(taskstring) =>
        put_results(return_val) =>
        result = true;
    /*
    return_val = task(taskstring) => trace("Return received : %s" % return_val) =>
        put_results(return_val) =>
        result = true; // => trace("Finished run");
    */
}


(string tasks) get_tasks()
{
    //tasks = python_r0_server("import swift_e",
    //                               "swift_e.get_tasks()");
    tasks = python_r0("import swift_e",
                      "swift_e.get_tasks()");
}


(boolean result) put_results(string results)
{
    python_r0("import swift_e",
              "swift_e.put_results(\"%s\")" % results) =>
        result = true ;//=> trace("Posting result %s" % results);
}


(boolean result ) make_tasks(int count)
{
    qname = python_r0("import swift_e",
                      "swift_e.make_tasks(%d)" % count) =>
        printf("Qname from maketasks : %s", qname) =>
        result = true;
}

(boolean result ) make_queues (string jobs_q, string results_q)
{
    qname = python_r0("import swift_e",
                      "swift_e.make_queues(\"%s\", \"%s\")" % (jobs_q, results_q)) =>
        //printf("Qname from maketasks : %s", qname) =>
        result = true;
}


loop(int jobmax) {

    foreach i in [0:jobmax+1:1] {
    //for (boolean b = true; b; b=c) {

        boolean c;
        tasks = get_tasks(); // => printf("Got task: %s", tasks);
        if (tasks == "DONE") {

            printf("Tasks all DONE. Exiting");
            c = false;

        } else {
            //trace("Run tasks %s " % tasks);
            c = run_tasks(tasks) ;//=> printf("Task status : %i", c);
            //c = put_results("result_foooo");
        }
    }
}

int jobmax = 100;

//make_tasks(jobmax) => loop(jobmax);
make_queues("tcp://127.0.0.1:5557", "tcp://127.0.0.1:5558")  => loop(jobmax);
