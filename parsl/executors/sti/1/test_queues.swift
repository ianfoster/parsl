
// WORKFLOW

//import python;
import io;
import string;
import python;
//import location;

(string output) python_r0(string code, string expr) "turbine" "0.1.0"
[ "set <<output>> [ turbine::python 1 <<code>> <<expr>> ]" ];

/*
(string output) python_r0_worker(string code, string expr) "turbine" "0.1.0"
[ "set <<output>> [ turbine::python 1 <<code>> <<expr>> ]" ];

@dispatch=CONTROL
(string output) python_r0_server(string code, string expr) "turbine" "0.1.0"
[ "set <<output>> [ turbine::python 1 <<code>> <<expr>> ]" ];
*/

(string result) task(string arguments)
{
    result = python_persist("import swift_e",
                            "repr(swift_e.task(\"%s\"))" % arguments) =>
        printf("task returned : %s", result);
}

(boolean result) run_tasks(string taskstring)
{
    return_val = task(taskstring) =>
        put_results(return_val) =>
        result = true;
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
        result = true;
}


(boolean result ) make_tasks(int count)
{
    qname = python_r0("import swift_e",
                           "swift_e.make_tasks(%d)" % count) =>
        printf("Qname from maketasks : %s", qname) =>
        result = true;
}




loop(int jobmax) {

    foreach i in [0:jobmax+1:1] {
    //for (boolean b = true; b; b=c) {

        boolean c;
        tasks = get_tasks() ;//=> printf("Got task: %s", tasks);
        if (tasks == "DONE") {

            c = false;

        } else {

            c = run_tasks(tasks) ;//=> printf("Task status : %i", c);

        }
    }
}

int jobmax = 30;

make_tasks(jobmax) => loop(jobmax);

/*
loop()
{
    for (boolean b = true; b; b=c)
        {
            boolean c;
            tasks = get_tasks() => printf("Got task: %s", tasks);

            if (tasks == "DONE")
                {
                    c = false;
                }
            else
                {
                    c = run_tasks(tasks) => printf("Task returned: %s", c);

                }

        }
}

loop();
*/
