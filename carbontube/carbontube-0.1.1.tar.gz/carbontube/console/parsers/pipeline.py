import argparse
import multiprocessing


parser = argparse.ArgumentParser(
    prog='carbontube pipeline',
    description="""executes an instance of the pipeline manager server.

    ::

      $ carbontube pipeline \\
          --sub-bind=tcp://0.0.0.0:6000 \\
          --pull-bind=tcp://0.0.0.0:5050

    """)

parser.add_argument(
    'path',
    default='examples/simple.py',
    help='path to the python file containing the phase'
)

parser.add_argument(
    'name',
    help='the pipeline name'
)

parser.add_argument(
    '--sub-bind',
    help='a valid address in the form: tcp://<hostname>:<port>'
)

parser.add_argument(
    '--sub-connect',
    action='append',
    help='a valid address in the form: tcp://<hostname>:<port>'
)

parser.add_argument(
    '--pull-bind',
    default=None,
    help='a valid address in the form: tcp://<hostname>:<port>'
)

parser.add_argument(
    '--pull-connect',
    action='append',
    help='sets one or more connect addresses in which this pipeline should pull from'
)
parser.add_argument(
    '--concurrency',
    default=multiprocessing.cpu_count() ** 2,
    type=int,
    help='how many concurrent jobs to run at a time',
)
