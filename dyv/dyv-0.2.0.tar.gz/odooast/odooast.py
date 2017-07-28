# -*- coding: utf-8 -*-

import ast
import os


class AstFile(object):

    data = {}
    def __init__(self, paths):
        for path in paths:
            file_content = open(path).read()
            obj = ast.parse(file_content)
            self.data[path] = []
            for item in ast.iter_child_nodes(obj):
                if type(item) == ast.ClassDef:
                    class_name = item.name
                    if item.bases and type(item.bases[0])==ast.Name:
                        class_base = ','.join([x.id for x in item.bases])
                    elif item.bases and type(item.bases[0])==ast.Attribute:
                        class_base = ','.join([x.attr for x in item.bases])
                    else:
                        continue
                    object_name = False
                    fields = {}
                    inherit = False
                    for child in ast.iter_child_nodes(item):
                        if type(child) == ast.Assign:
                            attributes = [x.id for x in child.targets]
                            if type(child.value) == ast.Str and '_name' in attributes :
                                object_name = child.value.s
                            elif type(child.value) == ast.Str and '_inherit' in attributes :
                                object_name = child.value.s
                                inherit = True
                            elif type(child.value) == ast.Call and child.value.func.value.id == 'fields':
                                for field in attributes:
                                    fields.setdefault(field, {'type': child.value.func.attr})
                    if object_name :
                        self.data[path].append((class_name, class_base, object_name, inherit, fields))


    def get_data(self):
        return self.data

    def get_models(self):
        models = []
        for path, data in self.data.iteritems():
            for item in data:
                models.append(item)
        return models


class AstDir(object):

    py_files = []
    xml_files = []
    def __init__(self, path):
        for root, dirs, files in os.walk(path):
            for name in files:
                file = os.path.join(root, name)
                if file.lower().endswith('.py'):
                    self.py_files.append(file)
                if file.lower().endswith('.xml'):
                    self.xml_files.append(file)

    def get_py_files(self):
        return self.py_files

    def get_xml_files(self):
        return self.xml_files
