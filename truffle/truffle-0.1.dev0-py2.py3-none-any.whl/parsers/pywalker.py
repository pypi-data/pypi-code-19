"""
@Author: AmoL Kapoor
Node walker.
"""
import ast


def _get_node_name(node):
    """Get all attribute and name ids for a node."""
    name = []
    while not isinstance(node, ast.Name):
        if isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Attribute):
            name = [node.attr] + name if len(name) else [node.attr]
            node = node.value
        elif isinstance(node, ast.Subscript):
            node = node.value
        else:
            break

    if isinstance(node, ast.Name):
        name = [node.id] + name if len(name) else [node.id]
    return name


def _get_args(node):
    if isinstance(node, ast.FunctionDef):
        return [arg.id for arg in node.args.args]
    elif isinstance(node, ast.ClassDef):
        return ['.'.join(_get_node_name(base)) for base in node.bases]


class FileWalker(ast.NodeVisitor):
    """Walk the file, populate the relevant DS."""

    def __init__(self, fname, root_dir):
        self.fname = fname
        self.root_dir = root_dir
        self.context = []
        self.var_name = []
        self.functions = {}
        self.variables = {}
        self.imported_modules = {}
        self.imported_functions = {}
        self.calls = {}

    def get_data(self):
        """Return data."""
        return (self.functions, self.variables, self.imported_modules,
                self.imported_functions, self.calls)

    def _check_imports(self, var_name):
        """Recursively check to make sure all imports are handled."""
        split_var_name = var_name.split('.')
        for asname, info in self.imported_modules.iteritems():
            if asname == split_var_name[0]:
                if asname == info:
                    split_var_name[0] = info
                else:
                    split_var_name[0], _ = self._check_imports(info)
                return  '.'.join(split_var_name), True

        for asname, info in self.imported_functions.iteritems():
            if asname == var_name:
                import_name, _ = self._check_imports(info[1])
                import_name = import_name + '.' + info[0]
                return import_name, True

        return var_name, False

    def _get_var_name(self, var_name_clone=None):
        """Get name from current var name list, checking against imports."""
        isimport = False
        if not var_name_clone:
            var_name_clone = list(self.var_name)
        # Handle direct imports, which only have a single function in the name.
        if (len(var_name_clone) == 2
                and var_name_clone[-1] in self.imported_functions):
            import_funcname, import_module = self.imported_functions[
                var_name_clone[-1]]
            import_module, isimport = self._check_imports(import_module)
            import_module = import_module
            var_name_clone[0] = import_module
            var_name_clone[-1] = import_funcname
        # Check to see if an import name exists in the variable name.
        else:
            var_name_clone[0], isimport = self._check_imports(var_name_clone[0])
        return var_name_clone, isimport

    def _process_import(self, node):
        """Process imports (asname - name) and store."""
        for alias in node.names:
            name = alias.name
            asname = alias.asname
            if not asname:
                asname = name
            if isinstance(node, ast.Import):
                self.imported_modules[asname] = name
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                self.imported_functions[asname] = (name, module)

    def _process_functiondef(self, node):
        """Process functions (fname.name.lineno - calls) and store."""
        function_name = '.'.join([self.fname] + self.context + [node.name])
        self.functions[function_name] = {
            'calls': {},
            'lineno': node.lineno,
            'calling_functions': [],
            'name': node.name,
            'fname': self.fname,
            'docstring': ast.get_docstring(node, clean=True),
            'scope': '.'.join(self.context),
            'args': _get_args(node)
        }

    def _process_call(self, node):
        """Process calls and store."""
        # Get the name of the call.
        var_name_clone = _get_node_name(node)
        var_name = '%s.%s.%d' % (self.fname, '.'.join(var_name_clone),
                                 node.lineno)

        # Check against imports.
        true_var_name_list, isimport = self._get_var_name(list(var_name_clone))

        # Check if the call source is the same file.
        if not isimport:
            var_name = '%s.%s.%d' % (self.fname, '.'.join(true_var_name_list), node.lineno)
            true_var_name_list = ([self.fname] + self.context + true_var_name_list)
        elif not '.'.join(true_var_name_list).startswith(self.root_dir):
            current_dir = '.'.join(self.fname.split('.')[:-1])
            true_var_name_list = [current_dir] + true_var_name_list

        # Add to calls list.
        true_var_name = '.'.join(true_var_name_list)
        self.calls[var_name] = {'source': true_var_name,
                                'caller': '.'.join([self.fname] + self.context +
                                                   [str(node.lineno)])}

        # Add to function calls.
        if self.context:
            last_scope = '.'.join([self.fname] + self.context)
            self.functions[last_scope]['calls'][true_var_name] = node.lineno

    def _process_variable(self, node):
        """Process variables (imported vars) and store."""
        var_name = '.'.join([self.fname] + self.context + self.var_name[::-1])
        if var_name not in self.variables:
            true_var_name_list, isimport = self._get_var_name(
                list(self.var_name[::-1]))
            if not isimport:
                true_var_name_list = ([self.fname] + true_var_name_list +
                                      [str(node.lineno)])
            elif not '.'.join(true_var_name_list).startswith(self.root_dir):
                current_dir = '.'.join(self.fname.split('.')[:-1])
                true_var_name_list = [current_dir] + true_var_name_list

            self.variables[var_name] = '.'.join(true_var_name_list)

        loaded_var_name = '%s.%d' % (var_name, node.lineno)
        self.variables[loaded_var_name] = self.variables[var_name]

    def visit_FunctionDef(self, node):
        self._process_functiondef(node)
        self.context.append(node.name)
        self.generic_visit(node)
        self.context.pop()

    def visit_ClassDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Call(self, node):
        self._process_call(node)
        self.generic_visit(node)

    def visit_Lambda(self, node):
        # lambdas are just functions, albeit with no statements
        self.context.append('lambda')
        self.generic_visit(node)
        self.context.pop()

    def visit_Attribute(self, node):
        self.var_name.append(node.attr)
        self.generic_visit(node)
        self.var_name.pop()

    def visit_Name(self, node):
        # TODO(ajkapoor): Current iteration doesnt properly handle variables.
        # Specifically, the names are on the wrong side of the attributes.
        # See: ...Test.thisisatest3.x.test_process_variable
        self.var_name.append(node.id)
        self._process_variable(node)
        self.generic_visit(node)
        self.var_name.pop()

    def visit_ImportFrom(self, node):
        self._process_import(node)
        self.generic_visit(node)

    def visit_Import(self, node):
        self.visit_ImportFrom(node)
