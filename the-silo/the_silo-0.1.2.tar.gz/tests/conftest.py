# the_silo py.test configuration

import os
import pytest


@pytest.fixture(scope='session')
def nuke():
    import nuke
    path = os.path.dirname(os.path.dirname(__file__))+'/the_silo/gizmos'
    nuke.pluginAddPath(path)
    return nuke


@pytest.fixture(scope='session')
def wrapper():
    from the_silo import wrapper
    return wrapper
