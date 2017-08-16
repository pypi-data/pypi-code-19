import asyncio
import os
import sys
import logging
import argparse
from iop.core.util import Stop


async def mont_flow(flow, script, penalty):
    logger = logging.getLogger(script[:-3])
    logger.info("started")
    while True:
        try:
            await flow(logger)
        except Stop:
            break
        except Exception as ex:
            logger.error("exception catch: %s", ex)
            await asyncio.sleep(penalty)
    logger.info("stopped")


async def monitor(routings, penalty):
    tasks = []
    for routing in routings:
        t = asyncio.get_event_loop().create_task(mont_flow(routing, script, penalty))
        tasks.append(t)
    await asyncio.wait(tasks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--penalty', type=float, default=3, help='Restart timeout after exception')
    parser.add_argument('scripts_location', default=os.getcwd(), nargs='?')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    root = logging.getLogger('ioio')
    location = args.scripts_location
    routings = []

    for script in os.listdir(location):
        path = os.path.join(location, script)
        if path.endswith('.py'):
            root.info('found %s', path)
            sys.path.append(os.path.abspath(path))
            md = __import__(script[:-3])
            if not hasattr(md, 'flow'):
                root.warning("<flow> method not found in %s", path)
            elif not asyncio.iscoroutinefunction(md.flow):
                root.warning("<flow> is not corouting function in %s", path)
            else:
                routings.append(md.flow)

    asyncio.get_event_loop().run_until_complete(monitor(routings, args.penalty))


if __name__ == '__main__':
    main()
