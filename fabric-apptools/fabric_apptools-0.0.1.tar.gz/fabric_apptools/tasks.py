from fabric.api import task
from fabric_apptools.appenv import set_environment

@task
def appenv(stage='development'):
    set_environment(stage)
