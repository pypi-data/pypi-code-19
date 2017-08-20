"""
Definitions wrap a openapiv3 spec file for traversal
Definitions can reference other definitions via the
    {"$ref": "file.yml#a/b/c"}
syntax
"""

import pprint
import textwrap

def is_ref(obj):
    """
    Determines if the object is a JSON Schema reference
    e.g. {"$ref": "filename.yml#a/path/here"}
    """
    return len(obj) == 1 and "$ref" in obj

class Definition:
    """
    >>> Definition({"foo":"bar"}, "foo.yml").foo
    'bar'

    >>> Definition({"foo":"bar"}, "foo.yml").bar
    Traceback (most recent call last):
     ...
    KeyError: "Path 'bar' did not exist in definition."

    >>> Definition({"a":{"b":{"$ref":"#c/d"}},
    ...             "c":{"d":{"e":{"$ref":"#h/i"}}},
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
        If the reference is another file, it defer's walking the reference to the other definition


        TESTS:

        >>> Definition({"a":{"b":{"$ref":"#c"}},
        ...             "c":{"d":"resolved val"}},
        ...     "foo.yml"
        ... ).ref("#a/b/d")
        'resolved val'

        >>> Definition({"a":{"b":{"$ref":"#c/d"}},
        ...             "c":{"d":{"e":"resolved val"}}},
        ...          "foo.yml"
        ... ).ref("#a/b/e")
        'resolved val'

        >>> Definition({"foo":{"bar":"spam"}}, "foo.yml").ref("#foo/bar")
        'spam'

        >>> Definition({"foo":{"bar":"spam"}}, "foo.yml").ref("other.yml#foo")
        Traceback (most recent call last):
         ...
        NotImplementedError: Cannot load external defition files.
        """

        if '#' not in ref:
            raise KeyError("$ref's must contain a root anchor '#'")

        # Case for filename.yml#a/b/c
        if not ref.startswith('#'):

            if not self._loader:
                raise NotImplementedError("Cannot load external defition files.")

            fragments = ref.split('#', maxsplit=1)
            filename = fragments[0]
            other_def = self._loader.load_definition(filename)

            return self._wrap_and_resolve(other_def.walk(fragments[1]))

        # default case for #a/b/c to walk from root of schema
        return self._wrap_and_resolve(self.walk(ref[1:], self._root))


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

    def walk(self, path, tree=None):
        """
        >>> Definition({"foo":{"bar":"spam"}}, "foo.yml").walk("foo/bar")
        'spam'

        >>> Definition({"foo":"spam", "bar":"aaa"}, "foo.yml").walk("bar")
        'aaa'
        """

        if tree is None:
            tree = self._schema


        # If we are traversing a {"$ref":"#ref"} object
        if is_ref(tree):
            tree = self.ref(tree["$ref"])

        # If there are further path segments
        if u"/" in path:
            key, destination = path.split('/', maxsplit=1)
            if key in tree:
                return self._wrap_and_resolve(
                    self.walk(destination, tree=tree[key])
                )
            else:
                raise KeyError(
                    "Path segment '%s' did not exist in definition. %s" %
                    (key, pprint.pformat(tree))
                )
        elif path in tree:
            return self._wrap_and_resolve(tree[path])

        raise KeyError("Path '%s' did not exist in definition." % (path))

    def _wrap_and_resolve(self, obj):
        if is_ref(obj):
            obj = self._resolve(obj)
        return self._wrap(obj)

    def _resolve(self, obj):
        return self.ref(obj["$ref"])

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

        >>> Definition({"a":{"b":{"$ref":"#c"}},
        ...             "c":{"d":"resolved val"}},
        ...      "foo.yml"
        ... )["a"]["b"]["d"]
        'resolved val'
        """

        return self.walk(key)

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
