import traceback
import sys
import signal
from subprocess import TimeoutExpired, Popen, PIPE
from child_process import ChildProcessContainer
import typing


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
                       report_timeout_proc: typing.Callable[[typing.ClassVar, Popen], None] = None) -> [bool, str, str]:
        success = False
        subprocedure = None
        max_wait = max_wait if max_wait is not None else self.max_wait
        report_timeout_proc = report_timeout_proc if report_timeout_proc is not None else self.report_timeout
        d = None
        try:
            with Popen(cmd, stdout=PIPE, stderr=PIPE) as proc:
                subprocedure = proc
                d = self.Doer(proc)
                cpc = ChildProcessContainer(d, '#Signal_Handler#', d.do_it)
                cpc.wait_for_it(max_wait)
                if cpc.is_alive() and cpc.is_running() and not proc.poll():
                    report_timeout_proc(proc)
                    return success
                success = True
        except TimeoutExpired:
            print('Timed out waiting for child process to complete')
            report_timeout_proc(subprocedure)
        return success, d.stdout if d is not None else None, d.stderr if d is not None else None
