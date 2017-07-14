import json
import os
import time
import traceback
from argparse import ArgumentParser

import requests


def is_service_ok(microservice_id):
    try:
        r = requests.get('http://localhost:8500/v1/agent/checks')
        checks = r.json()
        key = 'service:{}'.format(microservice_id)
        return checks[key]['Status'] in ('passing', 'warning')
    except Exception:
        traceback.print_exc()
        return False


SUPERVISOR_PROGRAMS = ['armada_agent', 'run_health_checks', 'register_in_service_discovery']


def parse_args():
    ap = ArgumentParser()
    ap.add_argument('-s', '--sleep', type=int, default=40,
                    help='Length of sleep period in seconds. Default 40s.')
    return ap.parse_args()


def main():
    args = parse_args()
    print('1. ===Prevent services from registering===')
    r = requests.get('http://localhost:8900/list', {'local': '1'})
    services = r.json()['result']
    services = sorted((service for service in services if ':' not in service['name']),
                      key=lambda s: (s['name'], s['microservice_id']))
    for i, service in enumerate(services, start=1):
        print('{}/{}\t{}\t{}\t{}'.format(i, len(services), service['name'], service['microservice_id'],
                                         json.dumps(service['tags'] or {})))

        os.system('docker exec -it {} supervisorctl stop {}'.format(service['container_id'],
                                                                    ' '.join(SUPERVISOR_PROGRAMS)))
        print('')

    print('')

    print('2. ===Restart consul===')
    os.system('armada ssh -l armada supervisorctl restart consul')
    print('3. ===Sleep before healing services===')
    print('Hint: Type Ctrl+C to skip sleeping phase.')
    try:
        sleep_in_seconds = args.sleep
        for i in range(sleep_in_seconds):
            print('Sleeping {} / {}'.format(i + 1, sleep_in_seconds))
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nSleep interrupted.\n')
        pass

    print('4. ===Healing services===')
    for i, service in enumerate(services, start=1):
        print('Healing: {}/{}\t{}\t{}\t{}'.format(i, len(services), service['name'], service['microservice_id'],
                                                  json.dumps(service['tags'] or {})))
        os.system('docker exec -it {} supervisorctl start {}'.format(service['container_id'],
                                                                     ' '.join(SUPERVISOR_PROGRAMS)))
        for retry in range(7):
            time.sleep(3)
            if is_service_ok(service['container_id']):
                print('Healed :)\n')
                break
        else:
            print('Not healed :(\n')
            time.sleep(3)


if __name__ == '__main__':
    main()
