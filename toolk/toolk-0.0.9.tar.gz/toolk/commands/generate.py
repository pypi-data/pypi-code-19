
"""The generate command."""


from json import dumps
from .base import Base
import sys
import glob
import pathlib
import os
import re
import time
import uuid

from .messages import headerString
from .messages import pathError
from .messages import vcConfirmation
from .messages import exitMessage
from .messages import doneMessage
from .messages import duplicateMessage

from ..templates.viewControllerTemplate import vc_template


class Generate(Base):
    """Generate a Swift/iOS components"""

    def run(self):
        # Print the header
        print(headerString)

        # Generate a ViewController
        if self.options["<blueprint>"] == "viewcontroller" or self.options["<blueprint>"] == "vc":

            # Check if we are at the right path
            self.check_path()
            time.sleep(0.5)

            # Confirm the creation of the ViewController
            name = self.options["<name>"]
            response = input(vcConfirmation.replace('{}',name.capitalize()))
            # Erease answer
            CURSOR_UP = '\033[F'
            ERASE_LINE = '\033[K'
            print(CURSOR_UP + ERASE_LINE)
            self.check_response(response)

            # Open template.xcodeproj/project.pbxproj
            path = '{}/project.pbxproj'.format(glob.glob('*.xcodeproj')[0])
            project_file = open(path,'r')
            project = project_file.read()

            # Check if Controller group exists
            controller_string = """name = Controllers;
			sourceTree = "<group>";"""
            if controller_string in project:
                print(" ✅  Controllers folder founded!")
            else:
                project = self.create_project_folder(project, "Controllers")

            print(" ✅  Loading viewController template.")
            time.sleep(0.2)

            # Load the template
            template = vc_template.replace("<name>", name.capitalize())

            # check if the file already exists
            if "{}ViewController.swift".format(name.capitalize()) in project:
                time.sleep(0.2)
                print(" 🛑  {}ViewController.swift already exists, shutting down.".format(name.capitalize()))
                time.sleep(0.2)
                print(duplicateMessage)
                sys.exit()

            # Create the file
            print(" ✅  Write file to disk.")
            time.sleep(0.2)
            filename = "./controllers/{}ViewController.swift".format(name.capitalize())
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(template)

            # Append the viewcontroller in the project
            project = self.create_file_project(project, "Controllers", name)
            print(" ✅  Adding viewController to Xcode project.")
            time.sleep(0.2)

            print(" ✅  Done!")
            time.sleep(0.2)
            print(doneMessage)

            # Create the viewcontroller folder if needed
            # pathlib.Path('/my/directory').mkdir(parents=True, exist_ok=True)

    def check_path(self):
        """Check if the commandline is in the appropriate project path"""
        if glob.glob('*.xcodeproj'):
            print(" ✅  Xcode project found: {} \n".format(glob.glob('*.xcodeproj')[0]))
        else:
            time.sleep(0.2)
            print(" 🛑 Wrong path.")
            time.sleep(0.2)
            print(pathError)
            sys.exit()

    def check_response(self, response):
        """Check if the answer is yes or no"""
        if response == "Y" or response == "y" or response == "YES" or response == "yes" or response == "Yes":
            pass
        else:
            print(exitMessage)
            sys.exit()

    def create_project_folder(self, project, folder_name):
        time.sleep(0.2)
        print(" ❗  {} folder doesn't exist yet in Xcode project.".format(folder_name))
        time.sleep(0.2)

        # Generate id
        group_id = self.generate_id()

        # Build the group block
        group_string = """\
        <group_id> /* <folder_name> */ = {
			isa = PBXGroup;
			children = ();
			name = <folder_name>;
			sourceTree = "<group>";
		};
        """
        group_string = group_string.replace('<group_id>', group_id)
        group_string = group_string.replace('<folder_name>', folder_name)

        # Append the block into the project
        query = "/* End PBXGroup section */"
        project = self.insert_string(project, group_string, project.rfind(query))

        # Find the name of the project
        pattern = r'remoteInfo = (.*);'
        match = re.search(pattern, project)
        time.sleep(0.2)
        print(" ✅  {} is the parent folder.".format(match.group(1)))
        time.sleep(0.2)

        # Find the main folder
        pattern = r'/\* '+match.group(1)+' \*/ = {.*children = \((.*)\).*path = '+match.group(1)+';'
        match = re.search(pattern, project, re.DOTALL)

        # Append group to the main folder
        group_string = "\n{} /* {} */,".format(group_id, folder_name)
        project = self.insert_string(project, group_string, match.span(1)[0])

        # Save project
        self.save_project(project)
        return project
        time.sleep(0.2)
        print(" ✅  {} folder created in Xcode project.".format(folder_name))
        time.sleep(0.2)


    def generate_id(self):
        return ''.join(str(uuid.uuid4()).upper().split('-')[1:])

    def insert_string(self, string, string_to_add, index):
        return string[:index] + string_to_add + string[index:]

    def create_file_project(self, project, folder_name, name):
        file_id = self.generate_id()

        # search controller group
        pattern = r'/\* '+folder_name+' \*/ = {\s*isa = PBXGroup;\s*children = \('
        match = re.search(pattern, project, re.DOTALL)
        # add the file in the group
        file_ref = "\n{} /*  {}ViewController.swift */,\n".format(file_id, name.capitalize())
        project = self.insert_string(project, file_ref, match.span(0)[1])
        # Save project
        self.save_project(project)

        # add to PBXBuildFile
        pattern = r'/\* End PBXBuildFile section \*/'
        match = re.search(pattern, project)
        buildfile_ref = "<id> /* <name>ViewController.swift in Sources */ = {isa = PBXBuildFile; fileRef = <file_id> /* <name>ViewController.swift */; };\n"
        buildfile_id = self.generate_id()
        buildfile_ref = buildfile_ref.replace("<id>", buildfile_id)
        buildfile_ref = buildfile_ref.replace("<file_id>", file_id)
        buildfile_ref = buildfile_ref.replace("<name>", name.capitalize())
        project = self.insert_string(project, buildfile_ref, match.span(0)[0])

        # add to PBXFileReference
        pattern = r'/\* End PBXFileReference section \*/'
        match = re.search(pattern, project)
        file_ref = "<id> /* <name>ViewController.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; name = <name>ViewController.swift; path = controllers/<name>ViewController.swift; sourceTree = SOURCE_ROOT; };\n"
        file_ref = file_ref.replace("<name>", name.capitalize())
        file_ref = file_ref.replace("<id>", file_id)
        project = self.insert_string(project, file_ref, match.span(0)[0])

        # add to PBXSourcesBuildPhase
        pattern = r'/\* Begin PBXSourcesBuildPhase section \*/\s*.* /\* .* \*/ = {\s*isa = PBXSourcesBuildPhase;\s*buildActionMask = .*;\s*files = \('
        match = re.search(pattern, project)
        file_ref = "<id> /* <name>ViewController.swift in Sources */,"
        file_ref = file_ref.replace("<id>", buildfile_id)
        file_ref = file_ref.replace("<name>", name.capitalize())
        project = self.insert_string(project, file_ref, match.span(0)[1])
        # Save project
        self.save_project(project)

        return project

    def save_project(self, project):
        # Save project
        path = '{}/project.pbxproj'.format(glob.glob('*.xcodeproj')[0])
        with open(path, "w") as f:
            f.write(project)
