import argparse
import os
import languages
import inspect

class NotSupportFormat(Exception):
    pass

class Compile(object):
    def __init__(self):
        self.args = self.parseArgs()
        self.format, self.obj = self.analyzeFile()

    def parseArgs(self):
        parser = argparse.ArgumentParser(description='auto compile code file')
        parser.add_argument('fullpath', metavar='File', type=str, help='File name of current document with full path.')
        return parser.parse_args()

    def analyzeFile(self):
        '''Analyze file types'''
        _, ext = os.path.splitext(self.args.fullpath)
        clsmembers = inspect.getmembers(languages, inspect.isclass)

        for name, obj in clsmembers:
            if ext in obj.format():
                # 返回类名称与实例对象
                return name, obj(self.args.fullpath)

        return ext,None

    def compile(self):
        if self.obj is None:
            raise NotSupportFormat('the format:{} is not support'.format(self.format))

        return self.obj.compile()


if __name__ == '__main__':
    compile = Compile()
    compile.compile()
    # compile()
