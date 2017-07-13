import os
import subprocess


def get_environment():
    """
    Get the environment parameter, depending on OS (Win/Unix).
    """
    if os.name == 'nt':  # not tested!
        environment = '--environment=WIN'
    else:
        environment = '--environment=UNIX'
    return environment


class Runner(object):
    """
    Setup to run envjasmine "specs" (tests).

    To use it, probably best to put it inside a normal python
    unit test suite, then just print out the output.
    """

    def __init__(self, rootdir=None, testdir=None, configfile=None,
                 browser_configfile=None):
        """
        Set up paths, by default everything is
        inside the "envjasmine" folder right here.
        Giving no paths, the sample specs from envjasmine will be run.
        XXX: it would be more practical if this raised an exception
             and you know you're not running the tests you want.

        parameters:
        testdir - the directory that holds the "mocks", "specs"
            and "include" directories for the actual tests.
        rootdir - the directory where the envjasmine code lives in.
        configfile - path to an extra js config file that is run for the tests.
        browser_configfile - path to an extra js config file for running
                    the tests in browser.
        """
        here = os.path.dirname(__file__)
        self.libdir = here
        self.rootdir = rootdir or os.path.join(here, 'envjasmine')
        self.testdir = testdir or self.rootdir
        self.configfile = configfile
        self.browser_configfile = browser_configfile
        self.runner_html = os.path.join(here, 'runner.html')

    def run(self, spec=None, capture_output=True):
        """
        Run the js tests with envjasmine.
        spec: (relative) path to a spec file (run only that spec)
        Returns the output
        """
        environment = get_environment()
        rhino_path = os.path.join(self.rootdir, 'lib', 'rhino', 'js.jar')
        envjasmine_js_path = os.path.join(self.rootdir, 'lib', 'envjasmine.js')
        rootdir_param = '--rootDir=%s' % self.rootdir
        testdir_param = '--testDir=%s' % self.testdir
        if self.browser_configfile and os.path.exists(self.browser_configfile):
            self.write_browser_htmlfile()

        command = [
            'java',
            '-Duser.timezone=US/Eastern',
            '-Dfile.encoding=utf-8',
            '-jar',
            rhino_path,
            envjasmine_js_path,
            '--disableColor',
            environment,
            rootdir_param,
            testdir_param
            ]

        if self.configfile and os.path.exists(self.configfile):
            command.append('--configFile=%s' % self.configfile)

        # if we were asked to test only some of the spec files,
        # addd them to the command line:
        if spec is not None:
            if not isinstance(spec, list):
                spec = [spec]
            command.extend(spec)

        shell = False
        stdout = None
        stderr = None
        if capture_output:
            # override if we want to capture the output of the test run
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE

        p = subprocess.Popen(command, shell=shell, stdout=stdout,
                             stderr=stderr)
        (res, stderr) = p.communicate()
        return res

    def write_browser_htmlfile(self):
        markup = self.create_testRunnerHtml()
        with open("browser.runner.html", 'w') as file:
            file.write(markup)

    def create_testRunnerHtml(self):
        with open(self.runner_html, 'r') as runner_html:
            html = runner_html.read()
            return html % {"libDir": os.path.normpath(self.libdir),
                           "testDir": os.path.normpath(self.testdir),
                           "browser_configfile": self.browser_configfile}
