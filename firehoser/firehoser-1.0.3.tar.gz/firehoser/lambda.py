import boto3
import os
import logging
import base64

# Standard logger
logger = logging.getLogger()

# Configure Firehose
firehose_client = boto3.client('firehose')
firehose_stream_name = os.getenv('FIREHOSE_STREAM_NAME')
delimiter = os.getenv('RECORD_DELIMITER', '\n')


def formatter(record, delimiter='\n'):
    """Decode a base63 string and append a new delimiter at the end."""
    decoded = base64.b64decode(record['kinesis']['data']).decode()
    return {
        'Data': decoded + delimiter
    }


def handler(event, context):
    """ Main lambda handler.

    The handler grabs events from Kinesis and forwards their content to
    Firehose after formatting them.

    Parameters
    ----------
    event: dict
        Contains Records grabbed from the Kinesis stream.
    """

    if not event['Records']:
        return 0

    records = [formatter(record, delimiter) for record in event['Records']]

    response = firehose_client.put_record_batch(
        DeliveryStreamName=firehose_stream_name,
        Records=records)

    failed_put_count = response.get('FailedPutCount')

    # Retry all the records
    if failed_put_count:
        raise IOError

    return len(event['Records'])
