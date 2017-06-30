''' Sample Executor for integration with SwiftT.

This follows the model used by `EMEWS <http://www.mcs.anl.gov/~wozniak/papers/Cancer2_2016.pdf>`_
to some extent.

'''
import concurrent.futures
from concurrent.futures import Future
import logging
import uuid
import threading
import weakref
import time
import sys, errno
import queue
from queue import Queue
import multiprocessing as mp
import pickle
from base64 import b64encode, b64decode
from ipyparallel.serialize import pack_apply_message, unpack_apply_message
from ipyparallel.serialize import serialize_object, deserialize_object

import parsl
from parsl.executors.base import ParslExecutor
import zmq_pipes

logger = logging.getLogger(__name__)

BUFFER_THRESHOLD = 1024*1024
ITEM_THRESHOLD = 1024

'''
Task_Q = Queue()
Results_Q = Queue()
'''
Task_Q = None
Results_Q = None


def log(token, s):
    print("python: %-10s %s" % (token+":", s))

def make_queues(jobs_q_url, results_q_url):

    global Task_Q
    global Results_Q
    print ("Jobs q : ", jobs_q_url)
    print ("Results q : ", results_q_url)

    Task_Q = zmq_pipes.JobsQIncoming(jobs_q_url)
    Results_Q = zmq_pipes.ResultsQOutgoing(results_q_url)

    return str(jobs_q_url)


def make_tasks(count):

    global Task_Q
    global Results_Q

    Task_Q = Queue()
    Results_Q = Queue()

    #print ("Jobs q : ", jobs_q_url)
    #print ("Results q : ", results_q_url)

    try:
        result = None
        with  open("131c58b1-ff2d-4b79-8dd7-b64f5f8d6b81.pkl", 'rb') as f:
            result = str(b64encode(f.read()))

        for i in range(0, count):
            print("Putting task")
            Task_Q.put(result)
        Task_Q.put("DONE")

    except queue.Empty:
        return "EMPTY"

    return str(Task_Q)

def get_tasks():
    ''' Get task received an serialized object comprised of [fn, args, kwargs]
    this serialized object is b64encoded here and returned as a string

    '''

    '''[TODO] Bad code, refactor
    '''
    global Task_Q

    print("Task_Q get called")
    result = None
    try:
        result = Task_Q.get(timeout=4)

        encoded_buf = str(b64encode(pickle.dumps(result)))

        return str(encoded_buf)

    except queue.Empty:
        #return str(Task_Q)
        return "DONE"

    #result = "Fooo"
    return result

def task(string_bufs):
    """ Executor.
    Args: name of the inputfile, which is a pickled object that contains
    the function to be executed, it's args, kwargs etc.
    name of the outputfile, where the outputs from the computation are to
    be pickled are written

    """

    #all_names = dir(__builtins__)
    user_ns   = globals()#locals()
    #user_ns.update( {'__builtins__' : {k : getattr(__builtins__, k)  for k in all_names} } )

    #log = open("debug.log", 'w+')
    #log.write("User_ns : \n")

    encoded_bufs = eval(string_bufs)
    #log.write("Encoded bufs : {0}\n".format( encoded_bufs))

    msg = pickle.loads(b64decode(encoded_bufs))

    task_id = msg['task_id']
    bufs = msg['bufs']

    #log.write("decoded task_id : {0}\n".format(task_id))
    #log.write("decoded bufs : {0}\n".format(bufs))
    #for key in user_ns.keys():
    #    log.write("    key:{0} value:{1}\n".format(key, user_ns[key]))
    #log.write( "Got bufs : {0}\n".format( bufs ))

    try:
        f, args, kwargs = unpack_apply_message(bufs, user_ns, copy=False)

    except Exception as e:
        return "Caught error : {0}".format(e)

    #log.close()
    #task_id = kwargs["task_id"]

    #log.write( "Got f : {0}\n".format( f ))
    #log.write( "Got args : {0}\n".format( args ))
    #log.write( "Got kwargs : {0}\n".format( kwargs ))

    #log.close()
    #raise TypeError

    #x = f(*args,**kwargs)
    #print(x)
    fname = getattr(f, '__name__', 'f')
    prefix     = "parsl_"
    fname      = prefix+"f"
    argname    = prefix+"args"
    kwargname  = prefix+"kwargs"
    resultname = prefix+"result"

    user_ns.update({ fname : f,
                     argname : args,
                     kwargname : kwargs,
                     resultname : resultname })

    code = "{0} = {1}(*{2}, **{3})".format(resultname, fname,
                                           argname, kwargname)


    #log.write("Executing code : {0}\n".format(code))

    try:
        #print("[RUNNER] Executing : {0}".format(code))
        exec(code, user_ns, user_ns)

    except Exception as e:
        logging.warn("Caught errors but will not handled %s", e)
        #return e
        #log.write("Caught exception in  code :{0} \n".format(e))
        #log.close()

        ret_value = e

    else :
        #print("Done : {0}".format(locals()))
        #print("[RUNNER] Result    : {0}".format(user_ns.get(resultname)))
        #return user_ns.get(resultname)
        ret_value = user_ns.get(resultname)


    return_data = {'task_id' : task_id,
                   'returns' : ret_value}

    ret_sbuf = pickle.dumps(return_data)
    ret_encoded = b64encode(ret_sbuf)

    #print ("Pickled : ", ret_sbuf)
    #print ("Encoded : ", ret_encoded)
    #log.write("Returning : {0}\n".format(ret_encoded))
    #log.write("type      : {0}\n".format(type(ret_encoded)))
    #log.close()
    return ret_encoded


def put_results(results):
    global Results_Q
    result = Results_Q.put(results)
    return "True"

class TurbineExecutor(ParslExecutor):
    ''' The Turbine executor. Bypass the Swift/T language and run on top off the Turbine engines
    in an MPI environment.

    Here's a simple diagram

                 |  Data   |  Executor   |   IPC      | External Process(es)
                 |  Flow   |             |            |
            Task | Kernel  |             |            |
          +----->|-------->|------------>|Outgoing_Q -|-> Worker_Process
          |      |         |             |            |    |         |
    Parsl<---Fut-|         |             |            |  result   exception
              ^  |         |             |            |    |         |
              |  |         |   Q_mngmnt  |            |    V         V
              |  |         |    Thread<--|Incoming_Q<-|--- +---------+
              |  |         |      |      |            |
              |  |         |      |      |            |
              +----update_fut-----+

    '''

    def _queue_management_worker(self):
        ''' The queue management worker is responsible for listening to the incoming_q
        for task status messages and updating tasks with results/exceptions/updates

        It expects the following messages:
        {
           "task_id" : <task_id>
           "result"  : serialized result object, if task succeeded
           ... more tags could be added later
        }

        {
           "task_id" : <task_id>
           "exception" : serialized exception object, on failure
        }

        We don't support these yet, but they could be added easily as heartbeat.

        {
           "task_id" : <task_id>
           "cpu_stat" : <>
           "mem_stat" : <>
           "io_stat"  : <>
           "started"  : tstamp
        }

        The None message is a die request.
        None

        '''
        self.Incoming_Q = zmq_pipes.ResultsQIncoming(self.results_q_url)

        while True:
            #print("Thread is active ", self.Incoming_Q)
            logger.debug("[MTHREAD] Management thread active")
            try:
                msg = self.Incoming_Q.get()
                #print("Got msg : ", msg)

            except queue.Empty as e:
                # timed out.
                print("Timeout")
                pass

            except IOError as e:
                logger.debug("[MTHREAD] caught broken queue : %s : errno:%s", e, e.errno)
                return

            except Exception as e:
                #logger.debug("[MTHREAD] caught unknown exception : %s", e)
                print("[MTHREAD] caught unknown exception : %s", e)
                pass

            else:

                if msg == None:
                    logger.debug("[MTHREAD] Got None")
                    return
                else:

                    d_msg = pickle.loads(b64decode(eval(msg)))

                    #print("DESERIALIZED : ", d_msg)

                    logger.debug("[MTHREAD] Got message : %s", d_msg)
                    task_fut = self.tasks[d_msg['task_id']]

                    if 'returns' in d_msg:
                        # TODO : More work on returns serialized objects rather
                        # than simple pickling
                        #result, remainder = deserialize_object(d_msg['returns'])
                        result = d_msg["returns"]
                        task_fut.set_result(result)

                    elif 'exception' in d_msg:
                        # TODO : This section is not implemented properly
                        #exception, remainder = deserialize_object(d_msg['exception'])
                        exception = d_msg['exception']
                        task_fut.set_exception(exception)

            if not self.isAlive:
                break

    # When the executor gets lost, the weakref callback will wake up
    # the queue management thread.
    def weakref_cb(_, q=None):
        ''' We do not use this yet
        '''

        q.put(None)

    def _start_queue_management_thread(self):
        ''' Method to start the management thread as a daemon.
        Checks if a thread already exists, then starts it.
        Could be used later as a restart if the management thread dies.
        '''

        logging.debug("In _start %s", "*"*40)
        if self._queue_management_thread == None:
            logging.debug("Starting management thread ")
            self._queue_management_thread = threading.Thread (target=self._queue_management_worker)
            self._queue_management_thread.daemon = True
            self._queue_management_thread.start()
        else:
            logging.debug("Management thread already exists, returning")


    def shutdown(self):
        ''' Shutdown method, to kill the threads and workers.
        '''

        self.isAlive = False
        logging.debug("Waking management thread")
        self.Incoming_Q.put(None) # Wake up the thread
        self._queue_management_thread.join() # Force join
        logging.debug("Exiting thread")
        self.worker.join()
        return True

    def __init__ (self, max_workers=2, thread_name_prefix='', jobs_q_url=None, results_q_url=None):
        ''' Initialize the thread pool
        Trying to implement the emews model.

        '''

        logger.debug("In __init__")
        self.mp_manager = mp.Manager()
        self.jobs_q_url = jobs_q_url
        self.results_q_url = results_q_url
        #self.Outgoing_Q = self.mp_manager.Queue()
        self.Outgoing_Q = zmq_pipes.JobsQOutgoing(jobs_q_url)
        #self.Incoming_Q = self.mp_manager.Queue()
        #self.Incoming_Q = Results_Q
        #self.Incoming_Q = zmq_pipes.ResultsQIncoming(results_q_url)
        self.isAlive   = True

        self._queue_management_thread = None
        self._start_queue_management_thread()

        logger.debug("Created management thread : %s", self._queue_management_thread)

        #self.worker  = mp.Process(target=runner, args = (self.Outgoing_Q, self.Incoming_Q))
        #self.worker.start()
        #logger.debug("Created worker : %s", self.worker)
        self.tasks   = {}

    def submit (self, func, *args, **kwargs):
        ''' Submits work to the thread pool
        This method is simply pass through and behaves like a submit call as described
        here `Python docs: <https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor>`_

        Returns:
              Future
        '''
        task_id = str(uuid.uuid4())

        logger.debug("Before pushing to queue : func:%s func_args:%s", func, args)

        self.tasks[task_id] = Future()

        # This is a really bad hack
        #kwargs['task_id'] = task_id


        fn_buf  = pack_apply_message(func, args, kwargs,
                                     buffer_threshold=1024*1024,
                                     item_threshold=1024)


        msg = {'task_id' : task_id,
               'bufs' : fn_buf}
        '''
        import pickle
        with open("{0}.pkl".format(task_id), 'wb') as f:
            print("Wrote to file {0}.pkl".format(task_id))
            pickle.dump(fn_buf, f)
        '''

        # Post task to the the outgoing queue
        self.Outgoing_Q.put(msg)

        # Return the future
        return self.tasks[task_id]
        #return str(self.Outgoing_Q)


    def scale_out (self, workers=1):
        ''' Scales out the number of active workers by 1
        This method is notImplemented for threads and will raise the error if called.
        This would be nice to have, and can be done

        Raises:
             NotImplemented exception
        '''

        raise NotImplemented

    def scale_in (self, workers=1):
        ''' Scale in the number of active workers by 1
        This method is notImplemented for threads and will raise the error if called.

        Raises:
             NotImplemented exception
        '''

        raise NotImplemented




if __name__ == "__main__" :

    print("Start")
    tex = TurbineExecutor()
    print("Done")
