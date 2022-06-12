import traceback
import sys
import signal


def print_stack(sig, frame):
    for thread_id, frame in sys._current_frames().items():
        print(dir(frame))
        print('\n--- Stack for thread {t} {n}---'.format(t=thread_id))
        traceback.print_stack(frame, file=sys.stdout)


class SignalHandler:
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
