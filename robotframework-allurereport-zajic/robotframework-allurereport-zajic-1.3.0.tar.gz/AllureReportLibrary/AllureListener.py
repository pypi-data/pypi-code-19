import os
import socket
import subprocess
import threading
import uuid
import webbrowser

from allure.common import AttachmentType
from allure.constants import Status
from allure.structure import TestLabel, Failure, Attach, TestSuite, TestStep
from allure.utils import now
from robot.libraries.BuiltIn import BuiltIn
from sqlalchemy.sql.expression import false

from .common import AllureImpl
from .constants import Robot, SEVERITIES, STATUSSES
from .structure import AllureProperties, TestCase, ContextType, ContextTypeState, HighLevelSuite, Test, \
    Step


class AllureListener(object):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, allurePropPath=None, source='Listener'):
        self.test_steps = []
        self.testsuite = None
        self.AllureProperties = None
        self.AllureImplc = None
        self.callstack = []
        self.AllurePropPath = allurePropPath
        self.AllureIssueIdRegEx = ''
        self.isFirstSuite = True
        self.setup_steps = []
        self.teardown_steps = []
        self.setup_phase = False
        self.teardown_phase = False
        self.tests = []
        self.current_context_type = ContextType.HIGH_LEVEL_SUITE
        self.high_level_suites = []
        self.current_high_level_suite = None
        self.current_test = None
        self.current_context_type = None
        self.current_step = None

        # Setting this variable prevents the loading of a Library added Listener.
        # I case the Listener is added via Command Line, the Robot Context is not
        # yet there and will cause an exceptions. Similar section in start_suite.
        try:
            AllureListenerActive = BuiltIn().get_variable_value('${ALLURE}', false)
            BuiltIn().set_global_variable('${ALLURE}', True)

        except:
            pass

    def start_suitesetup(self, name, attributes):
        start_test_attributes = {'critical': 'yes',
                                 'doc': 'Test Suite Setup section',
                                 'starttime': attributes['starttime'],
                                 'tags': [],
                                 'id': 's1-s1-t0',
                                 'longname': BuiltIn().get_variable_value('${SUITE_NAME}'),
                                 'template': ''
                                 }

        if len(str(start_test_attributes.get('doc'))) > 0:
            description = str(start_test_attributes.get('doc'))
        else:
            description = name

        current_test = TestCase(name=name,
                                description=description,
                                start=now(),
                                attachments=[],
                                labels=[],
                                #                 parameters=[],
                                steps=[])

        self.test_steps.append(current_test)
        return

    def end_suitesetup(self, name, attributes):
        end_test_attributes = {'critical': 'yes',
                               'doc': 'Test Suite Setup section',
                               'starttime': attributes['starttime'],
                               'endtime': attributes['endtime'],
                               'status': 'PASS',
                               'tags': [],
                               'id': 's1-s1-t0',
                               'longname': BuiltIn().get_variable_value('${SUITE_NAME}'),
                               'template': ''
                               }

        test = self.test_steps.pop()

        if attributes.get('status') == Robot.PASS:
            test.status = Status.PASSED
        elif attributes.get('status') == Robot.FAIL:
            test.status = Status.FAILED
            test.failure = Failure(message='error', trace='')
        elif end_test_attributes.get('doc') is not '':
            test.description = attributes.get('doc')

        if end_test_attributes['tags']:
            for tag in end_test_attributes['tags']:
                if tag.startswith('feature'):
                    test.labels.append(TestLabel(
                        name='feature',
                        value=tag.split(':')[-1]))
                if tag.startswith('story'):
                    test.labels.append(TestLabel(
                        name='story',
                        value=tag.split(':')[-1]))
                elif tag in SEVERITIES:
                    test.labels.append(TestLabel(
                        name='severity',
                        value=tag))
                elif tag in STATUSSES:
                    test.status = tag  # overwrites the actual test status with this value.

        self.threadId = threading.get_ident()

        test.labels.append(TestLabel(
            name='thread',
            value=str(self.threadId)))

        self.testsuite.tests.append(test)
        test.stop = now()
        return test

    def start_test(self, name, attributes):
        if len(str(attributes.get('doc'))) > 0:
            description = str(attributes.get('doc'))
        else:
            description = name

        new_test = Test()
        new_test.name = name
        new_test.description = description
        new_test.start = now()
        new_test.tags = attributes.get('tags')
        new_test.critical = attributes.get('critical')
        self.current_test = new_test
        self.current_high_level_suite.tests.append(new_test)
        self.current_context_type = ContextType.TEST
        return

    def end_test(self, name, attributes):
        if attributes.get('status') == Robot.PASS:
            self.current_test.status = Status.PASSED
        elif attributes.get('status') == Robot.FAIL:
            self.current_test.status = Status.FAILED

        self.current_test.message = attributes.get('message')
        self.current_test.stop = now()
        self.current_test.state = ContextTypeState.ENDED
        self.current_context_type = ContextType.HIGH_LEVEL_SUITE

        '''
        if attributes['tags']:
            for tag in attributes['tags']:
                # if re.search(self.AllureIssueIdRegEx, tag):
                #     test.labels.append(TestLabel(
                #         name=Label.ISSUE,
                #         value=tag))
                if tag.startswith('feature'):
                    test.labels.append(TestLabel(
                        name='feature',
                        value=tag.split(':')[-1]))
                if tag.startswith('story'):
                    test.labels.append(TestLabel(
                        name='story',
                        value=tag.split(':')[-1]))
                elif tag in SEVERITIES:
                    test.labels.append(TestLabel(
                        name='severity',
                        value=tag))
                elif tag in STATUSSES:
                    test.status = tag  # overwrites the actual test status with this value.

        self.PabotPoolId = BuiltIn().get_variable_value('${PABOTEXECUTIONPOOLID}')
        if (self.PabotPoolId is not None):
            self.threadId = 'PabotPoolId-' + str(self.PabotPoolId)
        else:
            self.threadId = threading.get_ident()

        test.labels.append(TestLabel(
            name='thread',
            value=str(self.threadId)))

        test.stop = now()
        '''
        return

    def start_suite(self, name, attributes):
        self.SuitSrc = '/root/robot'

        if (self.AllurePropPath is None):
            self.AllurePropPath = '/root/robot/allure.properties'

        if os.path.exists(self.AllurePropPath) is True:
            self.AllureProperties = AllureProperties(self.AllurePropPath)
            self.AllureIssueIdRegEx = self.AllureProperties.get_property('allure.issues.id.pattern')

        # Not using &{ALLURE} as this is throwing an error and ${ALLURE} gives the
        # desired dictionary in Allure as well.
        BuiltIn().set_global_variable('${ALLURE}', self.AllureProperties.get_properties())

        self.allurelogdir = "/root/robot/Allure"
        self.AllureImplc = AllureImpl(self.allurelogdir)

        if attributes.get('doc') is not '':
            description = attributes.get('doc')
        else:
            description = name

        new_suite = HighLevelSuite()

        new_suite.name = name
        new_suite.title = name
        new_suite.description = description
        new_suite.start = now()

        if self.current_high_level_suite is None:
            self.current_high_level_suite = new_suite
            self.high_level_suites.append(self.current_high_level_suite)
        else:
            new_suite.parent_suite = self.current_high_level_suite
            self.current_high_level_suite.suites.append(new_suite)
            self.current_high_level_suite = new_suite

        self.current_context_type = ContextType.HIGH_LEVEL_SUITE
        return

    def end_suite(self, name, attributes):
        self.current_high_level_suite.state = ContextTypeState.ENDED
        self.current_high_level_suite.stop = now()
        self.current_high_level_suite.setup = False
        self.current_high_level_suite.teardown = False
        self.current_high_level_suite.status = attributes.get('status')

        if self.current_high_level_suite.parent_suite is not None:
            self.current_high_level_suite = self.current_high_level_suite.parent_suite
        else:
            self.current_high_level_suite = None
        return

    def translate_to_allure(self, current_suite):
        if current_suite.tests:
            testsuite = TestSuite(name=current_suite.name,
                                  title=current_suite.name,
                                  description=current_suite.description,
                                  tests=[],
                                  labels=[],
                                  start=current_suite.start,
                                  stop=current_suite.stop)

            for test in current_suite.tests:
                test_case = TestCase(name=test.name,
                                     description=test.description,
                                     start=test.start,
                                     statusDetails="opopop",
                                     stop=test.stop,
                                     attachments=[],
                                     labels=[],
                                     steps=[],
                                     severity="Normal",
                                     status=test.status)
                test_case.labels.append(TestLabel(name='issue', value='TST-189'))

                # setup phase
                setup_steps = []
                parent_suite = current_suite
                while parent_suite is not None:
                    if parent_suite.setup_steps:
                        setup_steps.append(parent_suite.setup_steps)
                    parent_suite = parent_suite.parent_suite

                for steps in reversed(setup_steps):
                    for step in steps:
                        allure_step = TestStep(name=step.name,
                                               title=step.title,
                                               attachments=step.attachments,
                                               steps=[],
                                               start=step.start,
                                               stop=step.stop,
                                               status=step.status)
                        self.populate_step(step, allure_step)
                        test_case.steps.append(allure_step)

                # general phase
                for step in test.steps:
                    allure_step = TestStep(name=step.name,
                                           title=step.title,
                                           attachments=step.attachments,
                                           steps=[],
                                           start=step.start,
                                           stop=step.stop,
                                           status=step.status)
                    self.populate_step(step, allure_step)
                    test_case.steps.append(allure_step)

                # teardown phase
                teardown_steps = []
                parent_suite = current_suite
                while parent_suite is not None:
                    if parent_suite.teardown_steps:
                        teardown_steps.append(parent_suite.teardown_steps)
                    parent_suite = parent_suite.parent_suite

                for steps in teardown_steps:
                    for step in steps:
                        allure_step = TestStep(name=step.name,
                                               title=step.title,
                                               attachments=step.attachments,
                                               steps=[],
                                               start=step.start,
                                               stop=step.stop,
                                               status=step.status)
                        self.populate_step(step, allure_step)
                        test_case.steps.append(allure_step)

                testsuite.tests.append(test_case)

            logfilename = '%s-testsuite.xml' % uuid.uuid4()
            with self.AllureImplc._reportfile(logfilename) as f:
                self.AllureImplc._write_xml(f, testsuite)

        for suite in current_suite.suites:
            self.translate_to_allure(suite)

    def populate_step(self, step, current_allure_step):
        for current_step in step.steps:
            allure_step = TestStep(name=current_step.name,
                                   title=current_step.title,
                                   attachments=step.attachments,
                                   steps=[],
                                   start=current_step.start,
                                   stop=current_step.stop,
                                   status=current_step.status)
            current_allure_step.steps.append(allure_step)
            self.populate_step(current_step, allure_step)

    def start_keyword(self, name, attributes):
        step = Step()
        step.name = name
        step.title = attributes.get('kwname')
        step.doc = attributes.get('doc')
        step.tags = attributes.get('tags')
        step.start = now()

        if self.current_context_type == ContextType.HIGH_LEVEL_SUITE:
            if attributes.get('type') == 'Setup':
                self.current_high_level_suite.setup = True
                self.current_high_level_suite.teardown = True
                self.current_high_level_suite.setup_steps.append(step)
                self.current_step = step
            elif attributes.get('type') == 'Teardown':
                self.current_high_level_suite.setup = False
                self.current_high_level_suite.teardown = True
                self.current_high_level_suite.teardown_steps.append(step)
                self.current_step = step
            else:
                if self.current_high_level_suite.setup:
                    step.parent = self.current_step
                    self.current_step.steps.append(step)
                    self.current_step = step
                elif self.current_high_level_suite.teardown:
                    step.parent = self.current_step
                    self.current_step.steps.append(step)
                    self.current_step = step
        elif self.current_context_type == ContextType.TEST:
            if self.current_step is None:
                self.current_step = step
                self.current_test.steps.append(self.current_step)
            else:
                step.parent = self.current_step
                self.current_step.steps.append(step)
                self.current_step = step
        return

    def end_keyword(self, name, attributes):
        if attributes.get('status') == Robot.PASS:
            self.current_step.status = Status.PASSED
        elif attributes.get('status') == Robot.FAIL:
            self.current_step.status = Status.FAILED

        self.current_step.stop = now()
        self.current_step.state = ContextTypeState.ENDED

        if self.current_step.parent is not None:
            self.current_step = self.current_step.parent
        else:
            self.current_step = None

    def message(self, msg):
        pass

    def log_message(self, msg):
        startKeywordArgs = {'args': [],
                            'assign': [],
                            'doc': '',
                            'kwname': msg['message'],
                            'libname': 'BuiltIn',
                            'starttime': now(),
                            'tags': [],
                            'type': 'Keyword'}
        self.start_keyword('Log Message', startKeywordArgs)

        endKeywordArgs = {'args': [],
                          'assign': [],
                          'doc': '',
                          'elapsedtime': 0,
                          'endtime': now(),
                          'kwname': msg['message'],
                          'libname': 'BuiltIn',
                          'starttime': now(),
                          'status': 'PASS',
                          'tags': [],
                          'type': 'Keyword'}
        self.end_keyword('Log Message', endKeywordArgs)
        return

    def close(self):
        for suite in self.high_level_suites:
            self.translate_to_allure(suite)
        self.save_environment()
        return

    # Helper functions

    def save_environment(self):
        environment = {}
        environment['id'] = 'Robot Framework'
        environment['name'] = socket.getfqdn()
        environment['url'] = 'http://' + socket.getfqdn() + ':8000'

        # env_dict = ( \
        #    {'Robot Framework Full Version': get_full_version()}, {'Robot Framework Version': get_version()},
        #    {'Interpreter': get_interpreter()}, {'Python version': sys.version.split()[0]},
        #    {'Allure Adapter version': VERSION}, {'Robot Framework CLI Arguments': sys.argv[1:]},
        #    {'Robot Framework Hostname': socket.getfqdn()}, {'Robot Framework Platform': sys.platform} \
        #    )

        # for key in env_dict:
        #    self.AllureImplc.environment.update(key)

        self.AllureImplc.store_environment(environment)

    def allure(self, AllureProps):

        JAVA_PATH = AllureProps.get_property('allure.java.path')
        ALLURE_HOME = '-Dallure.home=' + AllureProps.get_property('allure.home')
        JAVA_CLASSPATH = '-cp "' + AllureProps.get_property('allure.java.classpath') + '"'
        ALLURE_LOGFILE = AllureProps.get_property('allure.cli.logs.xml')
        ALLURE_OUTPUT = '-o ' + AllureProps.get_property('allure.cli.logs.output')
        JAVA_CLASS = 'ru.yandex.qatools.allure.CommandLine'
        ALLURE_COMMAND = 'generate'
        ALLURE_URL = AllureProps.get_property('allure.results.url')

        allure_cmd = JAVA_PATH + ' ' + ALLURE_HOME + ' ' + JAVA_CLASSPATH + ' ' + JAVA_CLASS + ' ' + ALLURE_COMMAND + ' ' + ALLURE_LOGFILE + ' ' + ALLURE_OUTPUT

        if (AllureProps.get_property('allure.cli.outputfiles') == 'True'):
            FNULL = open(os.devnull, 'w')  # stdout=FNULL,
            subprocess.Popen(allure_cmd, stderr=subprocess.STDOUT, shell=True).wait()

        if (AllureProps.get_property('allure.results.browser.open') == 'True'):
            webbrowser.open(ALLURE_URL, new=0, autoraise=True)

    def attach(self, title, contents, attach_type=AttachmentType.PNG):
        """
        This functions created the attachments and append it to the test.
        """
        #         logger.console("attach-title: "+title)
        contents = os.path.join(BuiltIn().get_variable_value('${OUTPUT_DIR}'), contents)
        with open(contents, 'rb') as f:
            file_contents = f.read()

        attach = Attach(source=self.AllureImplc._save_attach(file_contents, attach_type),
                        title=title,
                        type=attach_type)

        self.test_steps[-1].attachments.append(attach)
        return
