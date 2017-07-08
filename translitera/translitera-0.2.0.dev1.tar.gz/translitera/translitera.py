# -*- coding: utf-8 -*-
# Copyright (C) Srikanth Anantharam 2016
"""
Created on Mon Aug  8 08:19:47 2016

@title:   translitera
@author:  Srikanth Anantharam <saprao@linux.com>
@purpose: Phonetic transliteration of text in Indic scripts into Latin/English
          characters
"""

import os
import sys
import argparse
import json

__author__ = "sria91"


class Translitera:

    def __init__(self, inputlang, outputlang):
        self.inputlang = inputlang
        self.outputlang = outputlang
        in2le_f = None

        # load the phonetic transliteration data
        if self.inputlang == "kn" and self.outputlang == "la":
            in2le_f = open(os.path.join(os.path.dirname(__file__),
                                        'kn2la.json'), encoding="utf-8")
        elif self.inputlang == "kn" and self.outputlang == "en":
            in2le_f = open(os.path.join(os.path.dirname(__file__),
                                        'kn2en.json'), encoding="utf-8")
        else:
            sys.stderr.write("LangError: unsupported language specified\n")
        self.in2le = json.load(in2le_f)
        in2le_f.close()

    @staticmethod
    def file_exists(path):
        if os.path.exists(path):
            if os.path.isfile(path):
                return True
            else:
                sys.stderr.write("PathError: '" + path +
                                 "' is not a file\n")
                return False
        else:
            sys.stderr.write("PathError: the file '" + path +
                             "' does not exist\n")
            return None

    @staticmethod
    def directory_exists(path):
        if os.path.exists(path):
            if os.path.isdir(path):
                return True
            else:
                sys.stderr.write("PathError: '" + path +
                                 "' is not a directory\n")
                return False
        else:
            sys.stderr.write("PathError: the directory '" + path +
                             "' does not exist\n")
            return None

    @staticmethod
    def file_or_directory_exists(path):
        if os.path.exists(path):
            if os.path.isfile(path):
                return True
            elif os.path.isdir(path):
                return True
            else:
                sys.stderr.write("PathError: '" + path +
                                 "' is not a file or directory\n")
                return False
        else:
            sys.stderr.write("PathError: the file or directory '" + path +
                             "' does not exist\n")
            return None

    def translitera(self, text):
        """the core logic to perform the transliteration"""
        phonemes = ''
        for i in range(len(text)):
            phonemes += self.in2le.get(text[i:i+2],
                                       self.in2le.get(text[i],
                                                      text[i]))
        return phonemes

    def cat(self, paths):
        for path in paths:
            if self.file_exists(path):
                with open(path) as f:
                    transliterated_text = self.translitera(f.read())
                    sys.stdout.write(transliterated_text)

    def file_or_directory_renamer(self, path):
        if self.file_or_directory_exists(path):
            pathwithoutext, ext = os.path.splitext(path)
            dirname = os.path.dirname(pathwithoutext)
            name = os.path.basename(pathwithoutext)
            newname = self.translitera(name)
            newabsname = os.path.join(dirname, newname + ext)
            os.rename(path, newabsname)

    def batch_renamer(self, path):
        if self.directory_exists(path):
            files = 0
            folders = 0
            contents = os.listdir(path)
            for name in contents:
                full_path = os.path.join(path, name)
                if os.path.isdir(full_path):
                    self.file_or_directory_renamer(full_path)
                    folders += 1
                elif os.path.isfile(full_path):
                    self.file_or_directory_renamer(full_path)
                    files += 1
            sys.stdout.write("translitera: " +
                             str(files) +
                             " file(s) and " +
                             str(folders) +
                             " folder(s) renamed successfully\n")


def main():
    parser = argparse.ArgumentParser(prog="translitera",
                                     description="phonetic transliteration of text in Indic scripts into"
                                                 " Latin/English characters")
    parser.add_argument("filenames", metavar="FILENAMES", nargs='*', help="filenames to transliterate and concatenate")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--text", metavar="TEXT",
                       help="transliterates the text in Indic script provided as an argument")
    group.add_argument("-r", "--rename", metavar="FILE_OR_DIRECTORY",
                       help="transliterates name of the file or directory specified by PATH")
    group.add_argument("-b", "--batch_rename", metavar="DIRECTORY",
                       help="transliterates name of the files within the specified directory")
    group.add_argument("-i", "--input_language", metavar="INPUT_LANGUAGE", default="kn",
                       help="language of the input text")
    group.add_argument("-o", "--output_language", metavar="OUTPUT_LANGUAGE", default="la",
                       help="language for the output text")
    args = parser.parse_args()

    if args.input_language not in ("kn",):
        sys.stderr.write("LangError: unsupported input language specified\n")
        return -1

    if args.output_language not in ("la", "en"):
        sys.stderr.write("LangError: unsupported output language specified\n")
        return -1

    t = Translitera(args.input_language, args.output_language)

    if args.filenames:
        t.cat(args.filenames)

    elif args.text:
        print(t.translitera(args.text))

    elif args.rename:
        t.file_or_directory_renamer(args.rename)

    elif args.batch_rename:
        t.batch_renamer(args.batch_rename)

    else:
        while True:
            text = os.sys.stdin.readline()
            if len(text) == 0:
                break
            else:
                os.sys.stdout.write(t.translitera(text))

    return 0
