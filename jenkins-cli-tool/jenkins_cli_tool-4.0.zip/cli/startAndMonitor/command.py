import click
import sys
import ast
import pprint
import jenkins as jenkinsapi
from time import sleep


@click.command()
@click.option('--job',required=True, help='Name of the job to start and monitor.')
@click.option('--token',default=None, help='Token to access the job.')
@click.option('--wait',required=True, help='Time to wait between each request to check the build\'s status.',type=int)
@click.option('--parameters',required=False, help='Job\'s parameters.')
@click.pass_obj
def startAndMonitor(jenkins,job, parameters, wait, token):
    """Starts and monitors a Jenkins job until it is finished."""
    pp = pprint.PrettyPrinter(indent=4)
    server = jenkinsapi.Jenkins(jenkins.url, username=jenkins.username, password=jenkins.password)
    try:
        next_build_number = server.get_job_info(job)['nextBuildNumber']
    except jenkinsapi.NotFoundException:
        print "NotFoundException when looking for job with name '%s'." % job
        exit(1)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    try:
        server.build_job(job, ast.literal_eval(parameters), token=token)
    except:
        pp.pprint(sys.exc_info())
        print "Please verify your parameters (especially choice parameters - are the values chosen authorized?)"
        exit(2)
    print "Build #%s of %s started." % (next_build_number, job)

    stop = False
    while not stop:
        try:
            build_info = server.get_build_info(job, next_build_number)
        except jenkinsapi.NotFoundException:
            print "NotFoundException when looking for build #%s : build probably still in the queue. Waiting %d sc until next retry." % (next_build_number, wait)
            sleep(wait)
            pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        else:
            if build_info['result'] == 'SUCCESS':
                print "Build #%s finished with result : SUCCESS." % next_build_number
                exit(0)
            elif build_info['result'] == 'FAILED':
                print "Build #%s finished with result : FAILED." % next_build_number
                stop = True
                exit(3)
            elif build_info['result'] == None and build_info['building'] == True:
                print "Build #%s is not finished yet. Waiting %d sc until next check." % (next_build_number,wait)
                sleep(wait)
            else:
                print "Unknown build result. Full trace below:"
                pp.pprint(build_info)
                exit(4)
