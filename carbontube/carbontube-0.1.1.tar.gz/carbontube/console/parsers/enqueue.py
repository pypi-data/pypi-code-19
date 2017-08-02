import argparse

parser = argparse.ArgumentParser(
    prog='carbontube enqueue',
    description='enqueues a job')

parser.add_argument(
    'address',
    help='a valid address in the form: tcp://<hostname>:<port>',
)

parser.add_argument(
    'name',
    help='the pipeline name'
)

parser.add_argument(
    'instructions',
    help='a json object with the instructions',
    default='{}',
    nargs='?'
)
