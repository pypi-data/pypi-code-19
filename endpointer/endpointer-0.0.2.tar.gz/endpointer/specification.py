"""
Specifications wrap an entire Open API v3 spec for an API
"""
from os import path, getcwd
import yaml
from .definition import Definition

class Specification:
    """
    Specifications represent an Open API v3 specification
    A specification consists of one or more definitions (yaml files)
    A specification acts as a loader for other definitions via load_definition()
    """

    def __init__(self, from_file):
        self.files = {}
        self.dirs = []

        self.root_definition = self.load_definition(from_file)


    def _traverse_paths_for(self, filename):

        # Current directory
        if path.isfile(path.abspath(filename)):
            base_directory = path.commonprefix([
                path.dirname(path.abspath(filename)),
                getcwd()
            ])
            self.dirs.append(base_directory)
            return base_directory
        # Try base dir's for files we've previously loaded
        # Lets definitions refer to each other relatively
        for known_file in self.files:
            full_known_file_path = path.abspath(known_file)
            known_directory = path.dirname(full_known_file_path)
            if path.isfile(known_directory + "/" + filename):
                return known_directory

        raise KeyError("Definition not found for %s" % filename)


    def load_definition(self, filename):
        """
        Loads YAML files and parses them as a Definition object
        """
        if filename not in self.files:
            directory = self._traverse_paths_for(filename)

            with open(directory+'/'+filename) as definition_file:
                spec = yaml.load(definition_file.read())
                self.files[filename] = Definition(spec, filename, loader=self)

        return self.files[filename]

    def ref(self, obj):
        """
        Resolves references across the specification,
            starting with the root definition.
        Definitions are responsivle for completing reference resolution between
            paths within their own file/definition. References to other files
            are resolved by the definition of that other file.
        """
        return self.root_definition.ref(obj)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
