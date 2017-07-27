import click
import boto3
import sys
import os
from io import BytesIO
import zipfile

from .iam import create_firehoser_role
from .iam import put_firehoser_role_policy

lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')
kinesis_client = boto3.client('kinesis')


def compress_file(path, mode=zipfile.ZIP_DEFLATED):
    with open(path, 'r') as zip_file:
        lambda_file_content = zip_file.read()
    lambda_io_buffer = BytesIO()
    zipFile = zipfile.ZipFile(lambda_io_buffer, 'w')
    zipFile.writestr('lambda.py', lambda_file_content, compress_type=mode)
    zipFile.close()
    lambda_io_buffer.seek(0)

    return lambda_io_buffer.read()


@click.group()
def firehoser():
    """Fowards records from Kinesis to Firehose."""
    pass


@firehoser.command()
@click.argument('kinesis_stream_name')
@click.argument('firehose_stream_name')
@click.option('--record_delimiter', '-d', default='\n')
def link(kinesis_stream_name, firehose_stream_name, record_delimiter):
    """Setup lambda to forwards events."""
    # Check the stream exists and grab information
    try:
        response = kinesis_client.describe_stream(StreamName=kinesis_stream_name)
    except kinesis_client.exceptions.ResourceNotFoundException as e:
        click.echo('Error: Stream {} not found'.format(kinesis_stream_name))
        sys.exit(-1)

    stream_arn = response['StreamDescription']['StreamARN']

    # Create Firehose role
    response = create_firehoser_role()
    role_arn = response['Role']['Arn']

    # Attach required policy
    response = put_firehoser_role_policy()

    # Read lambda zip
    directory = os.path.dirname(__file__)
    lambda_path = os.path.join(directory, 'lambda.py')

    # Compress in memory
    lambda_zip_file = compress_file(lambda_path)

    lambda_function_name = '{}_backup'.format(kinesis_stream_name)

    try:
        lambda_client.create_function(
            FunctionName=lambda_function_name,
            Runtime='python3.6',
            Role=role_arn,
            Handler='lambda.handler',
            Code={
                'ZipFile': lambda_zip_file,
            },
            Description='Lambda to backup {} Kinesis Stream'.format(kinesis_stream_name),
            Timeout=20,
            MemorySize=1024,
            Environment={
                'Variables': {
                    'FIREHOSE_STREAM_NAME': firehose_stream_name,
                    'RECORD_DELIMITER': record_delimiter
                }
            }
        )

    except lambda_client.exceptions.ResourceConflictException as e:
        click.echo('Error: A function named {} already exists!'.format(lambda_function_name))
        sys.exit(-1)

    # Add event source
    response = lambda_client.create_event_source_mapping(
        EventSourceArn=stream_arn,
        FunctionName=lambda_function_name,
        Enabled=True,
        BatchSize=500,
        StartingPosition='LATEST'
    )


@firehoser.command()
@click.argument('kinesis_stream_name')
@click.argument('firehose_stream_name')
def unlink(kinesis_stream_name, firehose_stream_name):
    """Destroy Lambda created with link."""
    function_name = '{}_backup'.format(kinesis_stream_name)

    lambda_arn = None

    # Grab Lambda
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        lambda_arn = response['Configuration']['FunctionArn']
    except lambda_client.exceptions.ResourceNotFoundException as e:
        click.echo('Warning: Lambda {} does not exist'.format(function_name))


    event_source_mappings = lambda_client.list_event_source_mappings()['EventSourceMappings']
    event_source_mapping_uuid = list(filter(lambda x: x.get('FunctionArn') == lambda_arn, event_source_mappings))[0]['UUID']
    response = lambda_client.delete_event_source_mapping(UUID=event_source_mapping_uuid)

    lambda_client.delete_function(FunctionName=function_name)


firehoser.add_command(link)
firehoser.add_command(unlink)
