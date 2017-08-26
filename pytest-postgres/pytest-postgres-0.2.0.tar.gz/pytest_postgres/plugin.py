import time
import uuid

import docker as docker_client
import psycopg2
import pytest


def pytest_addoption(parser):
    parser.addoption('--pg-image', action='store', default='postgres:latest',
                     help='Specify postgresql image name')
    parser.addoption('--pg-name', action='store', default=None,
                     help='Specify database container name to use.')
    parser.addoption('--pg-reuse', action='store_true',
                     help='Save database container at the end')


@pytest.fixture(scope='session')
def docker():
    return docker_client.from_env()


@pytest.yield_fixture(scope='session')
def pg_server(docker, request):
    pg_name = request.config.getoption('--pg-name')
    pg_image = request.config.getoption('--pg-image')
    pg_reuse = request.config.getoption('--pg-reuse')

    container = None
    port = None
    if not pg_name:
        pg_name = 'db-{}'.format(str(uuid.uuid4()))

    if pg_name:
        for item in docker.containers.list(all=True):
            if pg_name in item.name:
                container = item
                break

    if not container:
        docker.images.pull(pg_image)
        container = docker.containers.create(
            image=pg_image,
            name=pg_name,
            ports={'5432/tcp': None},
            detach=True
        )

    container.start()
    container.reload()

    host = container.attrs['NetworkSettings']['IPAddress']
    port = container.attrs['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort']

    pg_params = {'database': 'postgres', 'user': 'postgres',
                 'password': 'postgres', 'host': 'localhost', 'port': port}

    delay = 0.001
    for i in range(100):
        try:
            with psycopg2.connect(**pg_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT version();')
            break
        except psycopg2.Error:
            time.sleep(delay)
            delay *= 2
    else:
        pytest.fail('Cannot start postgres server')

    yield {'network': container.attrs['NetworkSettings'], 'params': pg_params}

    if not pg_reuse:
        container.kill()
        container.remove()
