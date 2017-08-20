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

        # Prevents the __setattr__ method from setting other attributes.
        self._constructed = True


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

    def paths(self):
        return list(self.root_definition["paths"].keys())

    def endpoints(self):
        """
        Returns a list of named endoints and references to their method and url
        Endoints are documented as `x-endpoint: <name>` fields.
        x-endpoint: <name> is expected to belong to an operation object
        See Open API Spec v3:
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#operationObject
        """

        if "paths" not in self.root_definition:
            raise ValueError(
                "Specification does not contain a `#paths` element."
            )

        endpoints = {}
        unknown_endpoints = []

        # FIXME: This would be much nicer if it were implemented usign iterators
        for url in self.root_definition["paths"]:
            for method in self.root_definition["paths"][url]:
                operation = self.root_definition["paths"][url][method]
                if "x-endpoint" in operation:
                    endpoint_name = operation["x-endpoint"]
                    if endpoint_name not in endpoints:
                        endpoints[endpoint_name] = {
                            path: [method]
                        }
                    elif path not in endpoints[endpoint_name]:
                        endpoints[endpoint_name][url] = [method]
                    else:
                        endpoints[endpoint_name][url].append(method)
                else:
                    unknown_endpoints.append((method, url))
        return endpoints



    def __contains__(self, key):
        """
        Provides `"some_key" in Specification()`
        """
        return any(item == key for item in self.root_definition)

    def __len__(self):
        """
        Provides len(Specification())
        """
        return len(self.files)

    def __getitem__(self, key):
        """
        Provides `Specification()["some_key"]`
        Resolves from the root_definition
        """

        return self.root_definition.walk(key)

    def __setitem__(self, key, value):
        """
        Provides `Specification()["some_key"] = "some value"`
        Note: Specifications cannot be modified
        """
        raise KeyError("Cannot modify key '%s'" % key)

    def __delitem__(self, key):
        """
        Provides `del Specification()["some_key"]`
        Note: Specifications cannot be modified
        """
        raise KeyError("Cannot delete key '%s'" % key)

    def __getattr__(self, attrib):
        """
        Provides `Specification().some_key"`
        Note: Useful only for simply named keys.
        """
        return self[attrib]

    def __delattr__(self, key):
        """
        Provides `del Specification().some_key`
        Note: Specifications cannot be modified
        """
        raise KeyError("Cannot delete attribute '%s'" % key)

    def __setattr__(self, key, value):
        """
        Provides `Specification().some_key = "some_value"`
        Note: Specifications cannot be modified
        """
        if not self.__dict__.get("_constructed"):
            super().__setattr__(key, value)
        else: raise KeyError("Cannot set attribute '%s'" % key)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
