import logging
import argparse
import os
import umodules.helper as helper

from umodules.command import ICommand


def create_project(project, project_path):

    #   create unity project
    logging.debug("- creating unity project folder [{0}]".format(project_path))
    os.makedirs(project_path)
    os.makedirs(project_path + '/Assets')
    os.makedirs(project_path + '/Assets/' + project.args.name)
    os.makedirs(project_path + '/Assets/' + project.args.name + 'Work')
    os.makedirs(project_path + '/Assets/' + project.args.name + 'Test')

    #   check for file in base template folder
    try:
        filename = project.args.template + ".yml"
        template_path = os.path.abspath(project.options['template_path'] + filename)
        logging.debug("- looking for project template [{0}]".format(template_path))
        if not os.path.exists(template_path):
            #   check for file in config template folder
            template_path = os.path.abspath(project.home_path + "/templates/" + filename)
            logging.debug("- looking for project template [{0}]".format(template_path))
            if not os.path.exists(template_path):
                logging.debug("- unable to locate the project template [{0}]".format(template_path))
                raise Exception("uModules Template [{0}] was not Found.".format(filename))

        logging.debug("- found project template [{0}]".format(template_path))

        #   copy and replace project name
        newfile = project.args.name + ".yml"
        newpath = "./" + newfile

        f1 = open(template_path, 'r')
        f2 = open(newpath, 'w')
        for line in f1:
            line = line.replace('$project_name$', project.args.name)
            line = line.replace('$project_name:lower$', project.args.name.lower())
            f2.write(line)
        f2.close()
        f1.close()

        #   check for gitignore template
        filename = "gitignore"
        template_path = os.path.abspath(project.options['template_path'] + filename)
        logging.debug("- looking for project template [{0}]".format(template_path))
        if not os.path.exists(template_path):
            #   check for file in config template folder
            template_path = os.path.abspath(project.home_path + "/templates/" + filename)
            logging.debug("- looking for project template [{0}]".format(template_path))
            if not os.path.exists(template_path):
                logging.debug("- unable to locate the project template [{0}]".format(template_path))
                raise Exception("uModules Template [{0}] was not Found.".format(filename))

        logging.debug("- found project template [{0}]".format(template_path))

        #   copy and replace project name
        newfile = project_path + "/.gitignore"
        newpath = "./" + newfile

        f1 = open(template_path, 'r')
        f2 = open(newpath, 'w')
        for line in f1:
            line = line.replace('$project_name$', project.args.name)
            line = line.replace('$project_name:lower$', project.args.name.lower())
            f2.write(line)
        f2.close()
        f1.close()

    except Exception as e:
        raise e


class Install(ICommand):

    def run(self, project):

            project_path = "./" + project.args.name

            #   check if the project path is already there
            if os.path.exists(project_path):
                if not project.args.force:
                    raise Exception("Project [{0}] already exists, use the --force to overwrite".format(project.args.name))
                else:
                    logging.debug("- using the force to overwrite existing project")
                    helper.clean_folder(project_path)

            create_project(project, project_path)

    def build(self, subparser):
        super().build(subparser)
        cmd = subparser.add_parser("new", help="...")
        cmd.set_defaults(func=self.run)
        cmd.add_argument(
            "--ignore-project",
            default=True,
            help=argparse.SUPPRESS
        )
        cmd.add_argument(
            "-t",
            "--template",
            dest="template",
            help="use a different template",
            default="default")
        cmd.add_argument(
            "name"
        )

        logging.debug("- command [new] has been added to argparse")

    def activate(self):
        super().activate()

