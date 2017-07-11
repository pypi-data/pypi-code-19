from marshmallow import Schema, fields, validate


class NestedClass(Schema):
    DetalleIVA = fields.Integer()


class NestedListTest(Schema):
    DesgloseIVA = fields.List(fields.Nested(NestedClass), required=True)


class ListTest(Schema):
    Llista = fields.List(fields.Integer, required=True)


list_model = ListTest()
obj = {
    'Llista': [1, 2, 3]
}
errors = list_model.validate(obj)
if errors:
    raise Exception('Errors found 1', errors)
else:
    print 'Data 1'
    dumpo = list_model.dump(obj).data
    print dumpo
    from dicttoxml import dicttoxml

    xml_from_dict = dicttoxml(dumpo, root=False, attr_type=False)
    print xml_from_dict
print ' """""""""""""""""""""""""""""'
nested_list_model = NestedListTest()
new_obj = {
    'DesgloseIVA': [
        {
            'DetalleIVA': 1
        },
        {
            'DetalleIVA': 2
        }
    ]
}
errors = nested_list_model.validate(new_obj)
if errors:
    raise Exception('Errors found 2', errors)
else:
    print 'Data 2'
    from pprintpp import pprint

    donald_dump = nested_list_model.dump(new_obj).data
    print donald_dump
    from lxml import etree
    from lxml import objectify

    xml_from_dict = dicttoxml(donald_dump, root=False, attr_type=False)
    print xml_from_dict
    xml_from_dict = xml_from_dict.replace('<item>', '')
    xml_from_dict = xml_from_dict.replace('</item>', '')
    print xml_from_dict
print ' *9***************** PROVA 3 ************'
nested_list_model = NestedListTest()
new_obj = {
    'DesgloseIVA': {
        'DetalleIVA': [
            {
                'Base': 1
            },
            {
                'Base': 2
            }
        ]
    }
}


class BaseImponible(Schema):
    Base = fields.Integer()


class NestedClass2(Schema):
    DetalleIVA = fields.List(fields.Nested(BaseImponible))


class NestedListTest2(Schema):
    DesgloseIVA = fields.Nested(NestedClass2)


nested_list_model = NestedListTest2()
errors = nested_list_model.validate(new_obj)
if errors:
    raise Exception('Errors found 2', errors)
else:
    print 'Data 2'
    from pprintpp import pprint

    donald_dump = nested_list_model.dump(new_obj).data
    print donald_dump
    from lxml import etree
    from lxml import objectify

    xml_from_dict = dicttoxml(donald_dump, root=False, attr_type=False)
    print xml_from_dict
    xml_from_dict = xml_from_dict.replace('<item>', '')
    xml_from_dict = xml_from_dict.replace('</item>', '')
    print xml_from_dict
