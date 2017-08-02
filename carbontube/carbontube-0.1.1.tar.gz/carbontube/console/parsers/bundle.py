import argparse
import multiprocessing


parser = argparse.ArgumentParser(
    prog='carbontube bundle',
    description='runs a pipeline server + internal phases in a bundle')

parser.add_argument(
    'path',
    help='path to the python file containing the phase'
)

parser.add_argument(
    'name',
    help='the pipeline name'
)
parser.add_argument(
    '--sub-bind',
    default='tcp://127.0.0.1:6000',
    help='a valid address in the form: tcp://<hostname>:<port>'
)
parser.add_argument(
    '--pull-bind',
    default='tcp://127.0.0.1:7000',
    help='a valid address in the form: tcp://<hostname>:<port>'
)

parser.add_argument(
    '--concurrency',
    default=multiprocessing.cpu_count() ** 2,
    type=int,
    help='how many concurrent jobs to run at a time',
)
