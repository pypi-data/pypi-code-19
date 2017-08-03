import argparse
import time
from tornado.httpclient import HTTPClient


def send_request(file, conductor):
    with open(file) as f:
        client = HTTPClient()
        response = client.fetch('{}/config'.format(conductor),
                                method='POST',
                                body=f.read())
    return response


def run():
    parser = argparse.ArgumentParser(
        description="Submit a job to the cluster via command line",
        prog='nfq-submit-cluster'
    )
    parser.add_argument('--conductor',
                        help='URL of the server',
                        default='http://localhost:8888')

    parser.add_argument('--file',
                        help='JSON file with the configuration',
                        required=True)

    args = parser.parse_args()

    response = send_request(args.file, args.conductor)

    if b'No active daemons' in response.body:
        print('No active daemons. Retrying after 10 s.')
        time.sleep(10)
        response = send_request(args.file, args.conductor)

    elif b'Not enough running daemons' in response.body:
        print('Not enough daemons. Retrying after 10 s.')
        time.sleep(10)
        response = send_request(args.file, args.conductor)

    print(response.body)

if __name__ == '__main__':
    run()
