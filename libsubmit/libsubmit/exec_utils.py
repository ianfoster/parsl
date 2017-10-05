import subprocess

def execute_wait (cmd, walltime):
    ''' Synchronously execute a commandline string on the shell.
    Args:
         - cmd (string) : Commandline string to execute
         - walltime (int) : walltime in seconds, this is not really used now.

    Returns:
         A tuple of the following:
         retcode : Return code from the execution, -1 on fail
         stdout  : stdout string
         stderr  : stderr string

    Raises:
         None.
    '''
    retcode = -1
    stdout = None
    stderr = None
    try :
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        proc.wait(timeout=walltime)
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        retcode = proc.returncode

    except Exception as e:
        print("Caught exception : {0}".format(e))
        logger.warn("Execution of command [%s] failed due to \n %s ",  (cmd, e))

    return (retcode, stdout.decode("utf-8"), stderr.decode("utf-8"))

def execute_no_wait (cmd, walltime):
    ''' Synchronously execute a commandline string on the shell.
    Args:
         - cmd (string) : Commandline string to execute
         - walltime (int) : walltime in seconds, this is not really used now.

    Returns:
         A tuple of the following:
         retcode : Return code from the execution, -1 on fail
         stdout  : stdout string
         stderr  : stderr string

    Raises:
         None.
    '''
    retcode = -1
    stdout = None
    stderr = None
    try :
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        pid = proc.pid

    except Exception as e:
        print("Caught exception : {0}".format(e))
        logger.warn("Execution of command [%s] failed due to \n %s ",  (cmd, e))

    return pid, proc
