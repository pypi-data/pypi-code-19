import argparse

parser = argparse.ArgumentParser(
    prog='carbontube web --host=0.0.0.0 --port=5000 --host=0.0.0.0',
    description='runs the web dashboard')

parser.add_argument(
    '-H', '--host',
    help='the host where the http server should listen',
    default='0.0.0.0',
)
parser.add_argument(
    '-p', '--port',
    help='the port where the http server should listen',
    default=5000,
    type=int
)
parser.add_argument(
    '-r', '--redis-uri',
    help='redis://[:<password>@]<hostname>[:<port>][/<db>]',
    default='redis://127.0.0.1:6379',
)
parser.add_argument(
    '--pipeline',
    help='the name of the pipeline',
)
