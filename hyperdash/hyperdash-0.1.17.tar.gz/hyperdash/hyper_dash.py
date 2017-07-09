# Python 2/3 compatibility
from __future__ import absolute_import, division, print_function, unicode_literals
from threading import Thread

import json
import logging
import time
import uuid

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from twisted.internet.defer import inlineCallbacks

from .sdk_message import create_run_started_message
from .sdk_message import create_run_ended_message
from .sdk_message import create_log_message


# Python 2/3 compatibility
__metaclass__ = type


INFO_LEVEL = 'INFO'
ERROR_LEVEL = 'ERROR'


class HyperDash:
    """HyperDash monitors a job and manages capturing IO / server comms.

    This class is designed to be run in its own thread and contains an instance
    of code_runner (which is running the job) and server_manager (for talking
    to the server.)
    """

    def __init__(
        self,
        job_name,
        code_runner,
        server_manager_class,
        io_bufs,
        std_streams,
        custom_api_key_getter=None,
    ):
        """Initialize the HyperDash class.

        args:
            1) job_name: Name of the current running job
            2) code_runner: Instance of CodeRunner
            4) server_manager_class: Server manager class
            5) io_bufs: Tuple in the form of (StringIO(), StringIO(),)
            6) std_streams: Tuple in the form of (StdOut, StdErr)
            7) custom_api_key_getter: Optional function which when called returns an API key as a string
        """
        self.job_name = job_name
        self.code_runner = code_runner
        self.server_manager_class = server_manager_class
        self.server_manager_instance = self.server_manager_class()
        self.out_buf, self.err_buf = io_bufs
        self.std_out, self.std_err = std_streams
        self.custom_api_key_getter = custom_api_key_getter
        self.programmatic_exit = False

        # Used to keep track of the current position in the IO buffers
        self.out_buf_offset = 0
        self.err_buf_offset = 0

        # SDK-generated run UUID
        self.current_sdk_run_uuid = None

        self.server_manager_instance.custom_init(self.custom_api_key_getter)

        def on_stdout_flush():
            self.capture_io()
            self.std_out.flush()

        def on_stderr_flush():
            self.capture_io()
            self.std_err.flush()

        self.out_buf.set_on_flush(on_stdout_flush)
        self.err_buf.set_on_flush(on_stderr_flush)

        # TODO: Support file
        self.logger = logging.getLogger("hyperdash.{}".format(__name__))

    def capture_io(self):
        self.out_buf.acquire()
        out = self.out_buf.getvalue()
        len_out = len(out) - self.out_buf_offset
        self.print_out(out[self.out_buf_offset:]) if len_out != 0 else None
        self.out_buf_offset += len_out
        self.out_buf.release()

        self.err_buf.acquire()
        err = self.err_buf.getvalue()
        len_err = len(err) - self.err_buf_offset
        self.print_err(err[self.err_buf_offset:]) if len_err != 0 else None
        self.err_buf_offset += len_err
        self.err_buf.release()

    def print_out(self, s):
        message = create_log_message(self.current_sdk_run_uuid, INFO_LEVEL, s)
        self.server_manager_instance.put_buf(message)
        self.std_out.write(s)

    def print_err(self, s):
        message = create_log_message(self.current_sdk_run_uuid, ERROR_LEVEL, s)
        self.server_manager_instance.put_buf(message)
        self.std_err.write(s)


    @inlineCallbacks
    def cleanup(self, exit_status):
        self.capture_io()

        self.server_manager_instance.put_buf(
            create_run_ended_message(self.current_sdk_run_uuid, exit_status),
        )

        yield self.server_manager_instance.cleanup(self.current_sdk_run_uuid)
        reactor.stop()

    def run(self):
        # Create a UUID to uniquely identify this run from the SDK's point of view
        self.current_sdk_run_uuid = str(uuid.uuid4())

        def user_thread():
            # Twisted callInThread API does not support the daemon flag, so we
            # wrap this in our own thread. Setting daemon = True is important
            # because otherwise if a user Ctrl-C'd, the program would not
            # terminate until the thread running the user's code had completed.
            code_thread = Thread(target=self.code_runner.run)
            code_thread.daemon = True
            code_thread.start()

        reactor.callInThread(user_thread)

        @inlineCallbacks
        def event_loop():
            try:
                self.capture_io()
                yield self.server_manager_instance.tick(self.current_sdk_run_uuid)
                exited_cleanly, is_done = self.code_runner.is_done()
                if is_done:
                    self.programmatic_exit = True
                    if exited_cleanly:
                        yield self.cleanup("success")
                    else:
                        yield self.cleanup("failure")
                    return
            except Exception as e:
                self.print_out(e)
                self.print_err(e)
                yield self.cleanup("failure")
                raise

        # Create run_start message before starting the LoopingCall to make sure that the
        # run_started message always precedes any log messages
        self.server_manager_instance.put_buf(
            create_run_started_message(self.current_sdk_run_uuid, self.job_name),
        )
        # now=False to give the ServerManager a chance to setup a connection before we try
        # and send messages.
        loop = LoopingCall(event_loop)
        loop.start(1, now=False)

        # Handle Ctrl+C
        def cleanup():
            loop.stop()
            # Best-effort cleanup, if we return a deferred the process hangs
            # and never exists. This is ok though because on the off chance
            # it doesn't make it through we'll catch it when the heartbeat
            # stops coming through
            if not self.programmatic_exit:
                self.server_manager_instance.send_message(
                    create_run_ended_message(self.current_sdk_run_uuid, "user_canceled"),
                    # Prevent "Unhandled error in Deferred:" from being shown to user
                    raise_exceptions=False
                )
        reactor.addSystemEventTrigger("before", "shutdown", cleanup)
        reactor.run()
