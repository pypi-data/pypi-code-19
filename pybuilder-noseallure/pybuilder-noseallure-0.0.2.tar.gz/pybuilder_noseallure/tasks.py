from pybuilder.core import task, init, depends, use_plugin, description
from pybuilder.errors import BuildFailedException
import subprocess, os.path
from pybuilder_noseallure.utils import getImportantDirs  # @UnresolvedImport
from pybuilder_noseallure.utils import prepareArgs  # @UnresolvedImport

use_plugin('python.core')

@init
def init_nose(project, logger):
    project.build_depends_on('nose')
    project.build_depends_on('nose-allure-plugin')

'''
    General usage of nose with allure is - nosetests -v maintests/test_module.py --with-allure --logdir=</path/to/logdir>
    This saves allure based log report input under the logdir
    Then we run allure specific commands to generate an allure report, and then open it on jetty server
    1. getImportantDirs will serve the location of logdir
    2. set_property - nose_with-allure, nose_logdir, and nose_where property will remain as is (since that is location of test dir)
    3. Rest execution logic of nosetests will remain same
    4. After nose tests execute, need to execute allure generate/open command:
        allure generate </path/to/logdir> --clean
        allure open
'''

@task('run_unit_tests')
@description('Run your entire test suite with Nose')
@depends('prepare')
def run_unit_tests(project, logger):
    # set cwd to project root
    test_dir,log_dir = getImportantDirs(project)

    logger.info("Test dir: %s" % test_dir)
    logger.info("Log dir: %s" % log_dir) 

    if os.path.exists(log_dir) == False:
        os.makedirs(log_dir)

    logger.debug("Setting initial nose properties")

    project.set_property('nose_where', test_dir)
    project.set_property("nose_with-allure", True)
    project.set_property("nose_logdir", log_dir)

    if project.get_property('verbose'):
        project.set_property('nose_nocapture', True)
        project.set_property('verbose', True)

    logger.debug("Collecting nose properties")

    args = ['nosetest']

    args = prepareArgs(project)
    args.insert(0, 'nosetests')

    for arg in args:
        logger.info('Nose arg: %s' % arg)

    noseEnv = os.environ.copy()
    cwd = os.getcwd()
    project_main_path = cwd + "\\src\\main\\python"
    noseEnv["PYTHONPATH"] = project_main_path

    logger.info("Launching nosetests")
    noseProc = subprocess.Popen(args, stdout=subprocess.PIPE, env=noseEnv)

    while noseProc.poll() is None:
        l = noseProc.stdout.readline()
        logger.debug(l)

    if noseProc.returncode != 0:
        logger.error('Unit tests failed with exit code %s' % noseProc.returncode)
        raise BuildFailedException('Unit tests did not pass')