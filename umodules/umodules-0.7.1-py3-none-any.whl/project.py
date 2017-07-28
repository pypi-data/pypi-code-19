#   Copyright 2016, SpockerDotNet LLC

import logging
import io
import yaml
import os
import dotmap


def load(filename, tokens):
    """
    Load a Project From a File

    Foo bar

    :param filename: The fully qualified Path and Filename to Load
    :return:
    """
    logging.debug(filename)
    logging.debug(tokens)

    #   check if the project file exists
    try:
        logging.debug("- looking for project config file [{0}]".format(filename))
        if not os.path.exists(filename):
            logging.debug("- unable to locate the project configuration file [{0}]".format(filename))
            raise Exception("uModules Project Configuration File [{0}] was not Found.".format(filename))

        #   open the file
        file = io.open(filename)
        text = file.read()

        #   replace tokens
        text = __replace_tokens(text, tokens)

        #   convert contents to yaml
        contents = yaml.load(text)

        #   munch the project
        project = __munch_project(contents)

        #   finalize
        project = __finalize_project(project)

        #   validate and finalize the project
        __validate_project(project)

    except Exception as e:
        raise e

    #   return the project
    return project


def __munch_project(contents):
    return dotmap.DotMap(contents)


def __finalize_project(project):
    #   set default module type for main
    if 'type' not in project.main:
        project.main.type = project.default_type

    project.main = __check_module_includes(project.main)
    project.main.is_main = True

    #   if name is missing use project
    if 'name' not in project:
        project.name = project.project

    #   when project is missing use the name attribute
    #   (backwards compatibility)
    if 'project' not in project:
        project.project = project.name

    #   default type
    if 'default_type' not in project:
        project.default_type = "git"

    #   set default module type for module_types
    for module in project.modules:
        if 'type' not in module:
            module.type = project.default_type
        if 'name' not in module:
            module.name = module.module
        module = __check_module_includes(module)
        if 'active' not in module:
            module.status = True
        module.is_main = False

    return project


def __replace_tokens(text, tokens):
    for token in tokens:
        search = "$" + token + "$"
        repl = tokens[token]
        text = text.replace(search, repl)
    return text


def __check_module_includes(module):
    if 'includes' not in module:
        module.includes = []
        inc = dotmap.DotMap()
        inc.dir = 'Assets/{0}'.format(module.name)
        module.includes.append(inc)

    for include in module.includes:
        if 'todir' not in include:
            include.todir = 'Assets/{0}'.format(module.name)

    return module


def __validate_project(project):
    #   error!
    if 'name' not in project and 'project' not in project:
        raise Exception("Project Configuration is Missing [name] or [project] Attribute")

    #   error!
    if 'unity_path' not in project:
        raise Exception("Project Configuration is Missing [unity_path] Attribute")

    #   error!
    project.unity_path = os.path.abspath(project.unity_path)
    logging.debug('- checking [unity_path] parameter [{0}]'.format(os.path.abspath(project.unity_path)))
    if not os.path.exists(project.unity_path):
        raise Exception("Project Configuration Attribute [unity_path] is Not Valid")

    #   error!
    if 'unity_packages_path' not in project:
        raise Exception("Project Configuration is Missing [unity_packages_path] Attribute")

    #   error!
    if not os.path.exists(project.project_path):
        raise Exception("Project Configuration Attribute [project_path] is Not Valid")

    #   error!
    project.unity_packages_path = os.path.abspath(project.unity_packages_path)
    if not os.path.exists(project.unity_packages_path):
        raise Exception("Project Confirguration Attribute [unity_packages_path] is Not Valid")

    if 'type' in project:
        if project.type != 'git':
            raise Exception('Only GIT is Support for Main Type')

    for module in project.modules:
        if 'url' not in module:
            raise Exception('Module [{0}] is missing [url] Attribute'.format(module.module))
        for module_type in project.module_types:
            print(module_type)

