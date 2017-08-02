import argparse
import multiprocessing


parser = argparse.ArgumentParser(
    prog='carbontube phase',
    description="""executes an instance of the phase server.

    ::

      $ carbontube phase \\
          --pub-connect=tcp://127.0.0.1:6000 \
          --push-connect=tcp://192.168.0.10:3000 \
          --pull-connect=tcp://192.168.0.10:5050 \
          --pull-bind=tcp://0.0.0.0:5050 \
          phases/audio.py convert-to-mp3
    """)

parser.add_argument(
    'path',
    default='examples/simple.py',
    help='path to the python file containing the phase'
)

parser.add_argument(
    'job_type',
    help='the job type'
)

parser.add_argument(
    '--pub-connect',
    default='tcp://127.0.0.1:6000',
    help='a valid address in the form: tcp://<hostname>:<port>'
)

parser.add_argument(
    '--pull-bind',
    default='tcp://0.0.0.0',
    help='a valid address in the form: tcp://<hostname>[:<port>]'
)
parser.add_argument(
    '--pull-connect',
    action='append',
    help='sets one or more connect addresses in which this phase should pull from'
)
parser.add_argument(
    '--push-connect',
    action='append',
    help='sets one or more connect addresses in which this phase should push to'
)

parser.add_argument(
    '--concurrency',
    default=multiprocessing.cpu_count() ** 2,
    type=int,
    help='how many concurrent jobs to run at a time',
)

parser.add_argument(
    '--timeout',
    default=1,
    type=float,
    help='timeout',
)
