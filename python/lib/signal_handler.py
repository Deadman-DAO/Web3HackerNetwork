import traceback
import sys
import os
import signal
from subprocess import TimeoutExpired, Popen, PIPE
from lib.child_process import ChildProcessContainer


def print_stack(sig, frame):
    for thread_id, frame in sys._current_frames().items():
        print(dir(frame))
        print('\n--- Stack for thread {t}---'.format(t=thread_id))
        traceback.print_stack(frame, file=sys.stdout)

class SignalHandler:
    class Doer:
        def __init__(self, proc):
            self.proc = proc
            self.stdout = None
            self.stderr = None

        def do_it(self):
            self.stdout, self.stderr = self.proc.communicate()

    def __init__(self):
        self.max_wait = 60

    def report_timeout(self, proc):
        print('Terminating long running thread  PID ', proc.pid if proc else '<None>')
        if proc:
            proc.kill()

    def abort(self, sig, frame):
        print('Abort signal received.  Leaving.')
        print_stack(sig, frame)
        gpl = getattr(self, 'get_process_list')
        if gpl and callable(gpl):
            for n in gpl():
                stop_meth = getattr(n, 'stop')
                if stop_meth and callable(stop_meth):
                    n.stop()
        stop_meth = getattr(self, 'stop')
        if stop_meth and callable(stop_meth):
            stop_meth(self)
        sys.exit(-1)

    def set_signal_handlers(self):
        signal.signal(signal.SIGUSR1 if sys.platform != "win32" else signal.SIGBREAK, print_stack)
        signal.signal(signal.SIGINT, self.abort)

    def execute_os_cmd(self, cmd,
                       max_wait: int = None,
                       report_timeout_proc=None) -> (bool, str, str):
        success = False
        subprocedure = None
        terminated = False
        max_wait = max_wait if max_wait is not None else self.max_wait
        if report_timeout_proc is None:
            report_timeout_proc = self.report_timeout
        d = None
        try:
            with Popen(cmd, stdout=PIPE, stderr=PIPE) as proc:
                subprocedure = proc
                d = self.Doer(proc)
                cpc = ChildProcessContainer(d, '#Signal_Handler#', d.do_it)
                cpc.wait_for_it(max_wait)
                if cpc.is_alive() and cpc.is_running() and not proc.poll():
                    terminated = True
                    report_timeout_proc(proc)
                    return success, 'wtf?', None
                success = True
        except OSError as e:
            print('Error executing command: ', cmd, ':', e)
            return False, 'That is not right', None
        except TimeoutExpired:
            print('Timed out waiting for child process to complete')
            report_timeout_proc(subprocedure)
        return success, d.stdout if d is not None else None, d.stderr if d is not None else None

    def boolean_damnit(self, val):
        ret_val = False
        if val and isinstance(val, str):
            val = val.lower().strip()
            if val == 'true':
                ret_val = True
        return ret_val

    def get_env_var(self, var_name, default_val=None, wrapper_method=None):
        val = os.environ.get(var_name, default=default_val)
        if val and wrapper_method and callable(wrapper_method):
            val = wrapper_method(val)
        return val

    def get_s3_base_dir(self):
        return self.get_env_var('S3_BASE_DIR', default_val='repo', wrapper_method=None)

