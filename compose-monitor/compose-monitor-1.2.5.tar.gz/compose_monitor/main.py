import argparse
import logging

import logger
from monitor import Monitor


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--compose-file", dest="path",
    default=".", help="Path to the docker-compose.yml")
parser.add_argument("-t", "--timeout", dest="timeout",
    default=10, help="Check&update timeout")
parser.add_argument("-e", "--external-scheduler", dest="scheduler",
    action="store_true", help="Don't use built-in timer")
parser.add_argument("-o", "--options", dest="options",
    help="Options for project")
parser.add_argument("--no-recreate", dest="norecreate",
    action="store_true", help="Don't recreate, only pull")
parser.add_argument("--no-deps", dest="nodeps",
    action="store_false", help="Don't restart services dependencies")
parser.add_argument("--affect-only-running", dest="running",
    action="store_true",
    help="Restart only running services and don't touch stopped")
parser.add_argument("-l", "--log", dest="log",
    help="Redirect logging to file")
args = parser.parse_args()

if args.log is not None:
    log = logging.getLogger(__name__)
    log.addHandler(logger.FileHandler(args.log))
    log.setLevel(logging.DEBUG)
else:
    log = logging.getLogger(__name__)
    log.addHandler(logger.StreamHandler())
    log.setLevel(logging.DEBUG)


def main():
    try:
        if args.options is None:
            monitor = Monitor(args.path, dict(),
                args.norecreate, args.nodeps, args.running, args.log)
        else:
            monitor = Monitor(args.path,
                dict(zip(args.options.split()[0::2],
                         args.options.split()[1::2])),
                args.norecreate, args.nodeps, args.running, args.log)
        log.info("Monitor created successfully")

        log.info("Starting of monitor...")
        monitor.run(int(args.timeout), args.scheduler)

    except KeyboardInterrupt:
        print('\nThe process was interrupted by the user')
        raise SystemExit

if __name__ == "__main__":
    main()
