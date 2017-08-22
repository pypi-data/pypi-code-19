#-*- coding: utf-8 -*-
import os
import StringIO
import sys

class Engine(object):
    def __init__(self):
        self.output = StringIO.StringIO()
        sys.stdout = self.output


        self.output_stack = []
        self.output_done = []

        self.result_file = None
        self.identifier = 0

    def prepareTemplateFile(self, template_file):
        with open(template_file, 'r') as source:
            template = StringIO.StringIO()

            for line in source:
                template.write(line)
        return template

    def find_path_to_result_file(self, template_file):
        resultfile = os.path.abspath(template_file)
        resultdir = os.path.dirname(resultfile)
        resultname = os.path.splitext(os.path.basename(resultfile))[0]
        return os.path.join(resultdir, resultname + '.py')

    def scopeBegin(self, name = None):
        if not name:
            self.identifier += 1
            name = 'script_' + str( self.identifier)

        output = StringIO.StringIO();
        sys.stdout = output

        scoped_result_file = os.path.join(self.result_files_path, name + '.py')

        self.output_stack.append( [ output, scoped_result_file]);

        return self.result_file, scoped_result_file

    def scopeEnd(self):
        self.output_done.append( self.output_stack.pop())

        if self.output_stack:
            output = self.output_stack[-1]
            sys.stdout = output[0];
        else:
            sys.stdout = self.output

    def prepareOutputs(self, template_file):
        self.result_files_path = os.path.dirname(template_file)

    def write(self, stream, filename, pre_script_definitions):
        size = stream.tell()
        if not size:
            return
        stream.seek(0)
        print 'Generating script %s.' % filename
        with open(filename, 'w') as resultfile:
            for key, value in pre_script_definitions.items():
                resultfile.write("%s = '%s'\n" % (key, value))

            for line in stream:
                resultfile.write(line)

    def run(self, template_file):
        self.result_file = os.path.abspath(template_file)
        self.prepareOutputs(template_file)

        globalVariables = {}
        try:
            template = self.prepareTemplateFile(template_file)
            code = compile(template.getvalue(), template_file, 'exec')
            template.close()
            exec(code, globalVariables)
        except (NameError, SyntaxError, TypeError) as e:
            sys.stderr.write( "Error in %s: %s.\n" % (os.path.realpath( template_file), str(e)))
            raise

        sys.stdout = sys.__stdout__

        pre_script_definitions = globalVariables[ 'global_pre_script_definitions']

        result_file = self.find_path_to_result_file(template_file)
        self.write(self.output, result_file, pre_script_definitions)

        for output, filename in self.output_done:
            self.write(output, filename, pre_script_definitions)

def main(args):
    if not os.path.isfile(args.template):
        sys.stderr.write("error: Could not find the template file " + args.template + '\n')
        sys.exit(1)
    engine().run(args.template)

__global_engine = None

def engine():
    global __global_engine
    if not __global_engine:
        __global_engine = Engine()

    return __global_engine

