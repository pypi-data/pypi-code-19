import argparse


parser = argparse.ArgumentParser(
    prog='carbontube streamer --pull=tcp://0.0.0.0:6000 --push=tcp://0.0.0.0:6060',
    description="""executes an instance of pull/push streamer for scaling pipelines and/or phases

    ::

      $ carbontube streamer \\
          --pull=tcp://0.0.0.0:5050 \\
          --push=tcp://0.0.0.0:6060 \\
          --pull-hwm=1000 \\
          --push-hwm=1000 \\

    """)

parser.add_argument(
    '--pull',
    default='tcp://0.0.0.0:6000',
    help=(
        'a valid ZeroMQ socket address where the Pull (SUB) will listen'
    )
)
parser.add_argument(
    '--push',
    default='tcp://0.0.0.0:6060',
    help=(
        'a valid ZeroMQ socket address where the Push (PUB) will listen'
    )
)
parser.add_argument(
    '--push-hwm',
    type=int,
    default=64,
    help=(
        'a hard limit on the maximum number messages that '
        'the streamer should hold in memory before dropping them.'
        'If you start losing messages, then you need more streamers. '
    )
)
parser.add_argument(
    '--pull-hwm',
    type=int,
    default=64,
    help=(
        'a hard limit on the maximum number messages that '
        'the streamer should hold in memory before dropping them.'
        'If you start losing messages, then you need more streamers. '
    )
)
