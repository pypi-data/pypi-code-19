"""
Definitions wrap a openapiv3 spec file for traversal
Definitions can reference other definitions via the
    {"$ref": "file.yml#a/b/c"}
syntax
"""

import pprint
import textwrap
import re

def is_ref(obj):
    """
    Determines if the object is a JSON Schema reference
    e.g. {"$ref": "filename.yml#a/path/here"}
    """
    return isinstance(obj, dict) and len(obj) == 1 and "$ref" in obj

class Definition(dict):
    """
    >>> Definition({"foo":"bar"}, "foo.yml").foo
    'bar'

    >>> Definition({"foo":"bar"}, "foo.yml").bar
    Traceback (most recent call last):
     ...
    KeyError: "Invalid JSON pointer. $ref pointer does not exist. Failed at path 'bar'"

    >>> Definition({"a":{"b":{"$ref":"#/c/d"}},
    ...             "c":{"d":{"e":{"$ref":"#/h/i"}}},
    ...             "h":{"i":"hello"}}, "foo.yml"
    ... ).a.b.e
    'hello'
    """

    def __init__(self, schema, filename, root=None, loader=None):
        if not isinstance(schema, dict):
            raise TypeError("schema must be a dictionary")
        if not isinstance(filename, str):
            raise TypeError("filename must be a string")

        self._schema = schema
        self._filename = filename
        self._loader = loader

        if root is None:
            root = schema
        self._root = root

        # Prevents the __setattr__ method from setting other attributes.
        self._constructed = True

    def attach(self, loader):
        """
        Attaches a loader (normally a Specification object) to this definition.
        Loaders must provide a load_definition(filename) method.
        Loaders are used to resolve references between definitions.
        """
        # yes this is a hack
        super().__setattr__("_loader", loader)

    def __repr__(self):
        """
        >>> Definition({"a":"b"}, "foo.yml") #doctest: +NORMALIZE_WHITESPACE
        <Definition
            schema={'a': 'b'},
            filename='foo.yml',
            root={'a': 'b'},
            loader=<class 'NoneType'>
        >
        """
        formatted_schema = pprint.pformat(self._schema)
        formatted_filename = pprint.pformat(self._filename)
        formatted_root = pprint.pformat(self._root)
        formatted_loader = type(self._loader)
        return textwrap.dedent(f"""\
        <Definition
            schema={formatted_schema},
            filename={formatted_filename},
            root={formatted_root},
            loader={formatted_loader}
        >""")

    def ref(self, ref):
        """
        Resolves a reference based on the root of the schema.
        If the reference is another file, it defer's walking the reference
            to the other definition object (provided by the
            loader's load_defition() method).

        TESTS / Examples

        >>> Definition({"a":{"b":{"$ref":"#/c"}},
        ...             "c":{"d":"resolved val"}},
        ...     "foo.yml"
        ... ).ref("#/a/b/d")
        'resolved val'

        >>> Definition({"a":{"b":{"$ref":"#/c/d"}},
        ...             "c":{"d":{"e":"resolved val"}}},
        ...          "foo.yml"
        ... ).ref("#/a/b/e")
        'resolved val'

        >>> Definition({"foo":"spam"}, "foo.yml").ref("#/foo")
        'spam'

        >>> Definition({"foo":{"bar":"spam"}}, "foo.yml").ref("#/foo/bar")
        'spam'

        >>> Definition({"foo":{"bar":"spam"}}, "foo.yml").ref("other.yml#/foo")
        Traceback (most recent call last):
         ...
        NotImplementedError: Cannot load external defition files.
        """

        if '#' not in ref and "/" not in ref:
            raise KeyError("Invalid $ref. Must start with '/' or an '#' anchor")


        if "#" in ref:
            # Case for filename.yml#a/b/c
            if not ref.startswith('#'):

                if not self._loader:
                    raise NotImplementedError(
                        "Cannot load external defition files."
                        )

                fragments = ref.split('#', maxsplit=1)
                filename = fragments[0]
                other_def = self._loader.load_definition(filename)

                return self._wrap_and_resolve(other_def.walk(fragments[1]))
            elif ref[0] == "#":
                return self._wrap_and_resolve(
                    # Strip the leadin #
                    self.pointer(ref[1:], self._root)
                    )
            else:
                # The '#' was elsewhere in the path - we don't implement this.
                raise NotImplementedError(
                    "Cannot locate $ref's containing char '#'."
                    )

        # default case for #/a/b/c to walk from root of schema
        return self._wrap_and_resolve(self.pointer(ref, self._root))


    def _wrap(self, value):
        """
        >>> isinstance(Definition({"foo":"bar"}, "foo.yml")._wrap({"foo":"bar"}), Definition)
        True

        >>> Definition({"foo":"bar"}, "foo.yml")._wrap("spam")
        'spam'
        """
        if isinstance(value, dict):
            return Definition(value, self._filename, root=self._root, loader=self._loader)
        return value


    def pointer(self, pointer, tree=None):
        """
        Evaluates or 'points' based on the JSON pointer specification.

        RFC6901 https://tools.ietf.org/html/rfc6901

        >>> Definition({"foo":"bar"}, "foo.yml").pointer("foo")
        Traceback (most recent call last):
         ...
        KeyError: "Invalid JSON pointer. Must reference the root '/'."

        >>> Definition({"foo":"bar"}, "foo.yml").pointer("/foo")
        'bar'

        >>> Definition({"foo":{"bar":"spam"}}, "foo.yml").pointer("/foo/bar")
        'spam'
        >>> Definition({"foo":"bar"}, "foo.yml").pointer("/foo/bar")
        Traceback (most recent call last):
         ...
        KeyError: "Invalid JSON pointer. $ref pointer does not exist. Failed at path 'bar'"
        """

        if tree is None:
            tree = self._schema

        # An empty pointer should return the whole tree.
        if len(pointer) == 0:
            return self._wrap_and_resolve(tree)

        if pointer[0] != '/':
            raise KeyError(f"Invalid JSON pointer. Must reference the root '/'.")

        # Source: http://www.regexpal.com/98146
        reference_pattern = r"(/(([^/~])|(~[01]))*)"
        reference_token = re.match(reference_pattern, pointer).group(0)

        assert reference_token != ""

        # This is a bit meta, I know.
        # If we are traversing a {"$ref":"#ref"} object
        if is_ref(tree):
            tree = self.ref(tree["$ref"])

        # If we've found /foo in /foo/bar, the next pointer is /bar
        next_pointer = pointer.replace(reference_token,"")
        if next_pointer == "":
            next_pointer = None # Makes subsequent code nicer to read

        reference_token = reference_token.replace("~1", '/')
        reference_token = reference_token.replace("~0", '~')

        # And logically the key we're searing for is "foo" from /foo
        reference_token_key = reference_token[1:] # strip the leading slash.

        # If we don't intend on traversing further and we don't have a value
        if not isinstance(tree, dict): # and next_pointer != "":

            # FIXME: Partial support for lists. Needs a full implementation.
            #special case it could be a list, attempt to resolve it
            if isinstance(tree, list):
                # self.ref() above has returned a [], use the current reference
                if reference_token_key[1:].isdigit():
                    return tree[int(reference_token_key[1:])]
                # we've pointed to a a list and the next pointer is a
                elif next_pointer and next_pointer[1:].isdigit():
                    return tree[int(next_pointer[1:])]
            pretty_tree = pprint.pformat(tree)
            raise KeyError(
                f"Invalid JSON pointer. " +
                f"$ref pointer does not exist. " +
                f"Failed at path '{reference_token_key}'" # in {pretty_tree}"
            )

        # if pointer is in current schema
        if reference_token_key in tree.keys():
            #if no more pointers, return
            if next_pointer is None:
                return self._wrap_and_resolve(tree[reference_token_key])
            #else recurse
            else:
                return self._wrap_and_resolve(
                    self.pointer(next_pointer, tree=tree[reference_token_key])
                )


        assert next_pointer != "" or reference_token_key not in tree
        pretty_tree = pprint.pformat(tree)
        raise KeyError(
            f"Invalid JSON pointer. " +
            f"$ref pointer does not exist. " +
            f"Failed at path '{reference_token_key}'" # in {pretty_tree}"
            )

    def walk(self, path, tree=None):
        """
        >>> Definition({"foo":{"bar":"spam"}}, "foo.yml").walk("/foo/bar")
        'spam'

        >>> Definition({"foo":"spam", "bar":"aaa"}, "foo.yml").walk("/bar")
        'aaa'

        """
        return self.pointer(path, tree)


    def _wrap_and_resolve(self, obj):
        if is_ref(obj):
            obj = self._resolve(obj)
        return self._wrap(obj)

    def _resolve(self, obj):
        return self.ref(obj["$ref"])


    def keys(self):
        """
        >>> Definition({"a":"b", "c":"d"}, "foo.yml").keys()
        ['a', 'c']
        """
        return list(self._schema.keys())

    def __contains__(self, key):
        """
        >>> "foo" in Definition({"foo":"bar"}, "foo.yml")
        True
        """
        # if key == "$ref":
        #     return key in self._resolve(key)

        return any(item == key for item in self._schema)

    def __len__(self):
        """
        >>> len(Definition({"foo":"bar"}, "foo.yml"))
        1
        """
        return len(self._schema)

    def __getitem__(self, key):
        """
        >>> Definition({"foo":"bar"}, "foo.yml")["foo"]
        'bar'

        >>> Definition({"foo":{"bar":"spam"}}, "foo.yml")["foo"]["bar"]
        'spam'

        >>> Definition({"a":{"b":{"$ref":"#/c"}},
        ...             "c":{"d":"resolved val"}},
        ...      "foo.yml"
        ... )["a"]["b"]["d"]
        'resolved val'
        """

        return self.pointer("/"+key)

    def __setitem__(self, key, value):
        """
        >>> Definition({"foo":"bar"}, "foo.yml")["foo"] = "spam"
        Traceback (most recent call last):
         ...
        KeyError: "Cannot modify key 'foo'"
        """
        raise KeyError("Cannot modify key '%s'" % key)

    def __delitem__(self, key):
        """
        >>> del Definition({"foo":"bar"}, "foo.yml")["foo"]
        Traceback (most recent call last):
         ...
        KeyError: "Cannot delete key 'foo'"
        """
        raise KeyError("Cannot delete key '%s'" % key)

    def __getattr__(self, attrib):
        """
        >>> Definition({"foo":"bar"}, "foo.yml").foo
        'bar'

        >>> Definition({"foo":{"bar":"spam"}}, "foo.yml").foo.bar
        'spam'
        """
        return self[attrib]

    def __delattr__(self, key):
        """
        >>> del Definition({"foo":"bar"}, "foo.yml").foo
        Traceback (most recent call last):
         ...
        KeyError: "Cannot delete attribute 'foo'"
        """
        raise KeyError("Cannot delete attribute '%s'" % key)

    def __setattr__(self, key, value):
        """
        >>> Definition({"foo":"bar"}, "foo.yml").foo = "spam"
        Traceback (most recent call last):
         ...
        KeyError: "Cannot set attribute 'foo'"
        """
        if not self.__dict__.get("_constructed"):
            super().__setattr__(key, value)
        else: raise KeyError("Cannot set attribute '%s'" % key)

    def schema(self):
        """
        >>> Definition({"foo":"bar"}, "foo.yml").schema()
        {'foo': 'bar'}
        """
        return self._schema

if __name__ == '__main__':
    import doctest
    doctest.testmod()
