import os

from invoke import Collection

from . import py, docker


collections = [py, docker]

ns = Collection()
for c in collections:
    ns.add_collection(c)


ns.configure(dict(
    project='testdocker',
    pwd=os.getcwd(),
    docker=dict(
        user=os.getenv('DOCKER_USER'),
        tag='%s/%s:latest' % (os.getenv('DOCKER_USER'), 'testdocker')
    )
))
