import argparse


parser = argparse.ArgumentParser(
    prog='carbontube forwarder --subscriber=tcp://0.0.0.0:6000 --publisher=tcp://0.0.0.0:6060',
    description="""executes an instance of subscriber/publisher forwarder for scaling communications between multiple minions and masters.

    ::

      $ carbontube forwarder \\
          --subscriber=tcp://0.0.0.0:6000 \\
          --publisher=tcp://0.0.0.0:6060 \\
          --subscriber-hwm=1000 \\
          --publisher-hwm=1000 \\

    """)

parser.add_argument(
    '--subscriber',
    default='tcp://0.0.0.0:6000',
    help=(
        'a valid ZeroMQ socket address where the Subscriber (SUB) will listen'
    )
)
parser.add_argument(
    '--publisher',
    default='tcp://0.0.0.0:6060',
    help=(
        'a valid ZeroMQ socket address where the Publisher (PUB) will listen'
    )
)
parser.add_argument(
    '--publisher-hwm',
    type=int,
    default=64,
    help=(
        'a hard limit on the maximum number messages that '
        'the forwarder should hold in memory before dropping them.'
        'If you start losing messages, then you need more forwarders. '
    )
)
parser.add_argument(
    '--subscriber-hwm',
    type=int,
    default=64,
    help=(
        'a hard limit on the maximum number messages that '
        'the forwarder should hold in memory before dropping them.'
        'If you start losing messages, then you need more forwarders. '
    )
)
