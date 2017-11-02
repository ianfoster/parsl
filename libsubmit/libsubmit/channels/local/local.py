from libsubmit.channels.channel_base import Channel
import subprocess
import os
import shutil
import logging

logger = logging.getLogger(__name__)

class LocalChannel (Channel):

    ''' This is not even really a channel, since opening a local shell is not heavy
    and done so infrequently that they do not need a persistent channel
    '''

    def __init__ (self, userhome=".", envs={}, scriptDir="./.scripts", **kwargs):
        '''
        KwArgs:
             userhome (string): (default='.') This is provided as a way to override and set a specific userhome
             envs (dict) : A dictionary of env variables to be set when launching the shell
             channel_script_dir (string): (default="./.scripts") Directory to place scripts
        '''
        self.userhome = os.path.abspath(userhome)
        self.hostname = "localhost"
        local_env     = os.environ.copy()
        self.envs     = local_env.update(envs)
        self.channel_script_dir = os.path.abspath(scriptDir)

    @property
    def script_dir(self):
        return self.channel_script_dir

    def execute_wait (self, cmd, walltime):
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
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    cwd=self.userhome,
                                    env=self.envs,
                                    shell=True)
            proc.wait(timeout=walltime)
            stdout = proc.stdout.read()
            stderr = proc.stderr.read()
            retcode = proc.returncode

        except Exception as e:
            print("Caught exception : {0}".format(e))
            logger.warn("Execution of command [%s] failed due to \n %s ",  (cmd, e))
            # Set retcode to non-zero so that this can be handled in the provider.
            if retcode == 0:
                retcode = -1

        return (retcode, stdout.decode("utf-8"), stderr.decode("utf-8"))

    def execute_no_wait (self, cmd, walltime):
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
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    cwd=self.userhome,
                                    env=self.envs,
                                    shell=True)
            pid = proc.pid

        except Exception as e:
            print("Caught exception : {0}".format(e))
            logger.warn("Execution of command [%s] failed due to \n %s ",  (cmd, e))

        return pid, proc

    def push_file(self, source, dest_dir):
        ''' If the source files dirpath is the same as dest_dir, a copy
        is not necessary, and nothing is done. Else a copy is made.
        '''

        local_dest = dest_dir + '/' + os.path.basename(source)

        # Only attempt to copy if the target dir and source dir are different
        if os.path.dirname(source) != dest_dir:
            try:
                shutil.copyfile(source, local_dest)
                os.chmod(local_dest, 0o777)

            except OSerror as e:
                raise FileCopyException(e, self.hostname)

        return local_dest


    def close(self ):
        ''' There's nothing to close here, and this really doesn't do anything

        Returns:
             - False, because it really did not "close" this channel.
        '''
        return False
