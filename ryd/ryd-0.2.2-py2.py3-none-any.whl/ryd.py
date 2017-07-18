# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

import glob
import os
import sys
import subprocess
from textwrap import dedent
from ruamel.std.pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString


class RYD(object):
    def __init__(self, args, config):
        self._args = args
        self._config = config

    def convert(self):
        for file_name in self._args.file:
            if '*' in file_name or '?' in file_name:
                for exp_file_name in sorted(glob.glob(file_name)):
                    self.convert_one(Path(exp_file_name))
                continue
            self.convert_one(Path(file_name))

    def convert_one(self, path):
        print(path)
        yaml = YAML()
        convertor = None
        for x in yaml.load_all(path):
            if convertor is None:
                assert 0.099 < float(x['version']) < 0.101
                if x['output'] == 'rst':
                    convertor = RSTConvertor(self, yaml, x)
                else:
                    raise NotImplementedError
                continue
            convertor(x)
        if convertor.updated:
            print('updated')
        convertor.write(path)
        # convertor.dump()
        sys.stdout.flush()

    def from_rst(self):
        for file_name in (Path(f) for f in self._args.file):
            ryd_name = file_name.with_suffix('.ryd')
            if ryd_name.exists() and not self._args.force:
                print('skipping', ryd_name)
                continue
            print('writing', ryd_name)
            with ryd_name.open('w') as fp:
                fp.write(dedent("""\
                ---
                version: 0.1
                output: rst
                fix_inline_single_backquotes: true
                # pdf: true
                --- |
                """))
                fp.write(file_name.read_text())


class Code(PreservedScalarString):
    yaml_tag = '!code'

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value)


class Comment(PreservedScalarString):
    yaml_tag = '!comment'

    @classmethod
    def from_yaml(cls, constructor, node):
        return ""


class Python(PreservedScalarString):
    yaml_tag = '!python'

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value)


class PythonPre(PreservedScalarString):
    yaml_tag = '!python-pre'

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value)


class Stdout(PreservedScalarString):
    yaml_tag = '!stdout'

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value)


class Convertor:
    def __init__(self, ryd):
        self._ryd = ryd
        self._tempdir = None
        self._tmpfile_nr = 0

    @property
    def tempdir(self):
        from ruamel.std.pathlib.tempdir import TempDir
        if self._tempdir is None:
            self._tempdir = TempDir(prefix='ryd', keep=3)
        return self._tempdir

    def update(self, s):
        return s

    def check_output(self, s):
        p = self.tempdir.directory / 'tmp_{}.py'.format(self._tmpfile_nr)
        self._tmpfile_nr += 1
        p.write_text(s)
        try:
            return subprocess.check_output(
                [os.environ.get('RYD_PYTHON', 'python'), str(p)],
                stderr=sys.stdout,
            ).decode('utf-8')
        except subprocess.CalledProcessError as e:  # NOQA
            return None


class RSTConvertor(Convertor):
    def __init__(self, ryd, yaml, md):
        super().__init__(ryd)
        self._yaml = yaml
        self._md = md
        self.data = []
        self.last_output = ''
        self.updated = False
        self.python_pre = ""
        yaml.register_class(Code)
        yaml.register_class(Comment)
        yaml.register_class(Python)
        yaml.register_class(PythonPre)
        yaml.register_class(Stdout)

    def __call__(self, s):
        # the read is at the end
        self._line = self._yaml.reader.line - s.count('\n') + 1
        sx = self.update(s)
        if sx:
            self.updated = True
            self.data.append(sx)
        else:
            self.data.append(s)

    def update(self, s):
        # if isinstance(s, PreservedScalarString) and not isinstance(s, Python):
        #     print(type(s))
        if isinstance(s, Python):
            return None
        # find all backquotes in document
        bqs = []
        lines = [0]  # character index in file to beginning of each line
        line = 0
        col = 0
        for idx, ch in enumerate(s):
            if ch == "`":
                bqs.append((idx, line, col))
            elif ch == '\n':
                lines.append(idx + 1)
                line += 1
                col = 0
                continue
            col += 1
        lines.append(None)  # for last line
        bqidx = 0
        last_line_displayed = -1
        while bqidx < len(bqs):
            lnr = bqs[bqidx][1]
            # ``pair of double backquotes`` -> code
            try:
                if s[lines[lnr]] == ' ' and s[lines[lnr] + 1] == ' ':
                    # first characters on line are spaces -> code/ryd example
                    bqidx += 1
                    continue
            except IndexError:
                print('error')
                pass
            if bqidx + 3 <= len(bqs) and \
               bqs[bqidx][0] + 1 == bqs[bqidx + 1][0] and \
               bqs[bqidx + 2][0] + 1 == bqs[bqidx + 3][0]:
                bqidx += 4
                continue
            # unmatched double backquotes
            # if bqidx + 1 <= len(bqs) and \
            #    bqs[bqidx][0] + 1 ==  bqs[bqidx+1][0]:

            # :cmd:`some string`
            if bqidx > 0 and s[bqs[bqidx][0] - 1] == ':':
                bqidx += 2
                continue
            # `some <url>`_
            try:
                if bqidx + 1 < len(bqs) and s[bqs[bqidx + 1][0] + 1] == '_':
                    bqidx += 2
                    continue
            except IndexError:
                pass  # probably end of file
            if lnr != last_line_displayed:
                print('{}: {}'.format(lnr + self._line, s[lines[lnr]:lines[lnr + 1]]), end='')

                last_line_displayed = lnr
            print(' ' * (-1 + len(str(lnr + self._line)) + bqs[bqidx][2]), '--^')
            bqidx += 1
        return None

    def write(self, path):
        outpath = path.with_suffix('.rst')
        with outpath.open('w') as fp:
            self.dump(fp)
        if self._args.pdf is False:
            return
        if self._args.pdf or self._md.get('pdf'):
            subprocess.check_output(['rst2pdf', str(outpath)])

    def dump(self, fp=sys.stdout):
        last_ended_in_double_colon = False
        last_code = False
        for d in self.data:
            if isinstance(d, (Python, Code)):
                if not last_ended_in_double_colon:
                    print('::\n', file=fp)
                for line in d.strip().splitlines():
                    print(' ', line, file=fp)
                last_code = True
                if isinstance(d, Python):
                    self.last_output = self.check_output(self.python_pre + d)
                    if self._ryd._args.verbose:
                        print('=========== output =========')
                        print(self.last_output, end='')
                        print('============================')
                    if self.last_output is None:
                        sys.exit(1)
            elif isinstance(d, PythonPre):
                # store prefix for following, incomplete, programs (not shown), so the can run
                self.python_pre = d
            else:
                drs = d.rstrip()
                if drs.endswith('::'):
                    last_ended_in_double_colon = True
                    d = type(d)(drs + '\n\n')
                if last_code:
                    last_code = False
                    print(file=fp)
                print(d, file=fp, end='')
                if isinstance(d, Stdout):
                    for line in self.last_output.strip().splitlines():
                        print(' ', line, file=fp)
                    last_code = True
                # print(file=fp)
