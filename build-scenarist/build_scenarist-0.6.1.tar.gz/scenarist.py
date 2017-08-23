#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
import sys
import argparse
import re
import subprocess
import os.path
import platform
import build_scenarist

version = "0.6.1"

info = build_scenarist.Info()

def script_name_parse(name):
    if not(bool(re.match("^(.+" + build_scenarist.scriptNameEnding + ")$", name))):
        msg = "%r bad script name " % name
        raise argparse.ArgumentTypeError(msg)
    return name

def real_path_to_dir(path):
    if not(bool(os.path.isdir(path))):
        msg = "%r no such dir " % path
        raise argparse.ArgumentTypeError(msg)
    return path

def path_to_dir(path):
    # написать проверку пути
    return path

def image_name_parse(imageName):
    # написать проверку имени docker-образа
    return imageName

def createParser ():
    # Создаем класс парсера
    parser = argparse.ArgumentParser(
            prog = 'scenarist',
            description = '''Utility for running platform specific scripts''',
            epilog = '''Lizin Aleksandr aka sogimu, email: sogimu@nxt.ru, 2017''',
            add_help = True
            )
 
    # Создаем группу параметров для родительского парсера,
    # ведь у него тоже должен быть параметр --help / -h
    parent_group = parser.add_argument_group (title='Settings')

    parent_group.add_argument ('--version', '-v',
                action='version',
                help = 'Print version',
                version='%(prog)s {}'.format (version))

    # Создаем группу подпарсеров
    subparsers = parser.add_subparsers (dest = 'command',
            title = 'Commands',
            description = 'Commands for first param %(prog)s')


    # Создаем парсер для команды create_config
    create_run_parser = subparsers.add_parser ('run',
            add_help = True,
            help = 'Run script for current OS',
            description = '''Command for running script for current OS''')

       # Создаем новую группу параметров
    run_group = create_run_parser.add_argument_group (title='run')
    # Добавляем параметры
    run_group.add_argument ('targets', type=str, nargs='+',
            help = 'Specify targets in script to run. The script will be choosen by current platform name or with help argument -os')

    run_group.add_argument ('--script', '-s', type=script_name_parse, required=False,
            help = "Specify script name for which os run. Example: Ubuntu_16.04. Format: " + "^(.+" + build_scenarist.scriptNameEnding + ")$" + ". Default script name on this platform is " + info.fullPlatformName())

    run_group.add_argument ('--scriptDir', '-d', type=real_path_to_dir, default="./scripts/", required=False,
            help = 'Path to directory with scripts. Example: ./scripts/')

    run_group.add_argument ('--image', '-i', type=image_name_parse, required=False,
            help = "Specify docker image name for run. Example: ubuntu_16.04.")

    run_group.add_argument ('--workspace', '-w', type=path_to_dir, required=False,
            help = "Specify path to dir where script should be run. Example: /repo")

    # Создаем парсер для команды create_config
    create_info_parser = subparsers.add_parser ('info',
            add_help = True,
            help = 'Get info about current platform',
            description = '''Command for geting info about current platform''')

    # Создаем новую группу параметров
    info_group = create_run_parser.add_argument_group (title='info')
    
    return parser

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
 
    if namespace.command == "run":
        # print namespace.os
        # print namespace.targets
        # print namespace.dir
        info = build_scenarist.Info()
        fullPlatformName = info.fullPlatformName()

        print(namespace)

        # scriptDir
        if namespace.scriptDir == None:
            userScriptsDir = scriptsDir
        else:
            userScriptsDir = namespace.scriptDir

        # script
        if namespace.script == None:
            scriptsVariants = build_scenarist.getScriptsVariants(userScriptsDir)
            scriptVariant = build_scenarist.chooseScriptVariant(fullPlatformName, scriptsVariants)
        else:
            scriptVariant = namespace.script[:-1 * len(build_scenarist.scriptNameEnding)]

        if userScriptsDir != None and scriptVariant != None and namespace.targets != None:
            pathToScript = os.path.join(userScriptsDir, scriptVariant + build_scenarist.scriptNameEnding)
            if os.path.isfile(pathToScript):
                if namespace.image != None and namespace.targets != None:
                    print build_scenarist.bcolors.HEADER + "Run targets of script: %s in docker image: %s " % (pathToScript, namespace.image) + build_scenarist.bcolors.ENDC
                    print '\n'.join(namespace.targets)
                    sys.stdout.flush()
                    build_scenarist.executeTargetsInImage(namespace.targets, pathToScript, namespace.image)
                else:
                    print build_scenarist.bcolors.HEADER + "Run targets of script: " + pathToScript + build_scenarist.bcolors.ENDC
                    print '\n'.join(namespace.targets)
                    sys.stdout.flush()
                    build_scenarist.executeTargets(namespace.targets, pathToScript)
            else:
                print build_scenarist.bcolors.FAIL + "Script " + pathToScript + " not found!" + build_scenarist.bcolors.ENDC
                sys.stdout.flush()
        else:
            print build_scenarist.bcolors.WARNING + "No script for current platform" + build_scenarist.bcolors.ENDC
            sys.stdout.flush()
        
    elif namespace.command == "info":
        info = build_scenarist.Info()
        print info.about_platform()
        sys.stdout.flush()

    else:
        parser.print_help()
